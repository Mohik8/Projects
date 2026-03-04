"""
RAG chat session.

On each question:
  1. Retrieve top-k relevant chunks from ChromaDB
  2. Build a prompt with conversation history + retrieved context
  3. Stream the response from Ollama (llama3 by default)
"""

from ingest import query_collection
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

DEFAULT_MODEL = "llama3"
MAX_HISTORY   = 6      # number of (Q, A) pairs to include in context
TOP_K         = 5      # number of chunks to retrieve

SYSTEM_PROMPT = """You are an AI document assistant that answers questions \
strictly based on the provided document context. If the answer is not found in the \
context, say so honestly — do not hallucinate. Be concise and accurate."""


def _build_prompt(history: list[tuple[str, str]], context: str, question: str) -> str:
    parts = [SYSTEM_PROMPT, "\n\n"]

    if context.strip():
        parts.append("=== Relevant document excerpts ===\n")
        parts.append(context.strip())
        parts.append("\n\n")

    if history:
        parts.append("=== Conversation history ===\n")
        for q, a in history[-MAX_HISTORY:]:
            parts.append(f"User: {q}\nAssistant: {a}\n")
        parts.append("\n")

    parts.append(f"User: {question}\nAssistant:")
    return "".join(parts)


class ChatSession:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model   = model
        self.history: list[tuple[str, str]] = []

    def reset(self):
        self.history.clear()

    def ask(self, question: str) -> tuple[str, list[str]]:
        """
        Ask a question. Returns (answer_text, list_of_source_strings).
        Streams tokens to stdout as they arrive.
        """
        # 1. Retrieve context
        chunks = query_collection(question, n_results=TOP_K)
        context = "\n---\n".join(
            f"[{c['source']}, p.{c['page']}]\n{c['text']}" for c in chunks
        )
        sources = list({f"{c['source']} (p.{c['page']})" for c in chunks})

        # 2. Build prompt
        prompt = _build_prompt(self.history, context, question)

        # 3. Stream from Ollama
        llm = Ollama(
            model=self.model,
            callbacks=[StreamingStdOutCallbackHandler()],
        )

        print("\nDocuChat: ", end="", flush=True)
        answer = llm.invoke(prompt)
        print()  # newline after stream ends

        # 4. Store history
        self.history.append((question, answer))
        if len(self.history) > MAX_HISTORY * 2:
            self.history = self.history[-MAX_HISTORY:]

        return answer, sources
