"""
Document ingestion pipeline.

Supported formats: PDF, plain text (.txt, .md)

Flow:
  1. Extract raw text
  2. Split into overlapping chunks
  3. Embed with nomic-embed-text via Ollama
  4. Store in ChromaDB with metadata (source filename, page, chunk index)
"""

from pathlib import Path
from typing import List
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

# ── Config ────────────────────────────────────────────────────────────────
CHROMA_PATH   = Path("./chroma_db")
COLLECTION    = "docuchat"
EMBED_MODEL   = "nomic-embed-text"   # pull with: ollama pull nomic-embed-text
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120

# ── ChromaDB client (persistent) ─────────────────────────────────────────
_client: chromadb.ClientAPI | None = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ── Embeddings (Ollama) ───────────────────────────────────────────────────
def _embedder():
    return OllamaEmbeddings(model=EMBED_MODEL)


# ── Text extraction ───────────────────────────────────────────────────────
def _load_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        loader = PyMuPDFLoader(str(path))
    elif suffix in (".txt", ".md"):
        loader = TextLoader(str(path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    return loader.load()


# ── Public API ────────────────────────────────────────────────────────────
def ingest_document(path: Path) -> int:
    """
    Ingest a file into ChromaDB.
    Returns number of chunks stored.
    """
    docs = _load_file(path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    if not chunks:
        return 0

    embedder = _embedder()
    texts = [c.page_content for c in chunks]
    embeddings = embedder.embed_documents(texts)

    col = _get_collection()
    ids = [f"{path.name}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": path.name,
            "chunk":  i,
            "page":   c.metadata.get("page", 0),
        }
        for i, c in enumerate(chunks)
    ]

    # Upsert (re-ingesting the same file replaces old chunks)
    col.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(chunks)


def query_collection(question: str, n_results: int = 5) -> list[dict]:
    """
    Return top-n relevant chunks for a question.
    Each result: {"text": str, "source": str, "page": int}
    """
    embedder = _embedder()
    q_emb = embedder.embed_query(question)
    col = _get_collection()

    results = col.query(
        query_embeddings=[q_emb],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    out = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        out.append({"text": text, "source": meta.get("source", "?"), "page": meta.get("page", 0)})
    return out


def list_documents() -> List[str]:
    """Return unique source document names in the collection."""
    col = _get_collection()
    total = col.count()
    if total == 0:
        return []
    results = col.get(include=["metadatas"], limit=total)
    sources = sorted({m["source"] for m in results["metadatas"] if "source" in m})
    return sources


def delete_document(name: str) -> int:
    """Remove all chunks for a given source document name."""
    col = _get_collection()
    results = col.get(where={"source": name}, include=["metadatas"])
    ids = results["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)
