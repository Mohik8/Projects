"""
DocuChat – chat with any PDF using a fully local RAG pipeline.

Architecture:
  PDF → text chunks → embeddings (nomic-embed-text via Ollama)
       → ChromaDB vector store → similarity search
       → context + question → LLM (llama3 via Ollama) → answer
"""

import sys
import os
from pathlib import Path
from ingest import ingest_document, list_documents, delete_document
from chat import ChatSession


BANNER = """
╔══════════════════════════════════════════════════════╗
║         AI Document Assistant                       ║
║   Chat with your PDFs. 100% offline. No API keys.  ║
╚══════════════════════════════════════════════════════╝
"""

HELP = """
Commands:
  /load  <path>          Ingest a PDF or .txt file into the knowledge base
  /docs                  List all ingested documents
  /rm    <doc_name>      Remove a document from the knowledge base
  /new                   Start a fresh conversation (clears history)
  /model <name>          Switch Ollama model (default: llama3)
  /help                  Show this message
  /quit                  Exit

Or just type a question to chat with your loaded documents.
"""


def main():
    print(BANNER)
    print("Type /help for commands or /load <file> to get started.\n")

    session = ChatSession()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/quit":
                print("Goodbye!")
                break

            elif cmd == "/help":
                print(HELP)

            elif cmd == "/load":
                if not arg:
                    print("Usage: /load <path>")
                else:
                    path = Path(arg.strip())
                    if not path.exists():
                        print(f"  ✗ File not found: {path}")
                    else:
                        print(f"  Ingesting {path.name} …")
                        count = ingest_document(path)
                        print(f"  ✓ Stored {count} chunks from '{path.name}'")

            elif cmd == "/docs":
                docs = list_documents()
                if docs:
                    print(f"\n  Ingested documents ({len(docs)}):")
                    for d in docs:
                        print(f"    • {d}")
                else:
                    print("  No documents ingested yet. Use /load <file>")
                print()

            elif cmd == "/rm":
                if not arg:
                    print("Usage: /rm <doc_name>")
                else:
                    n = delete_document(arg.strip())
                    print(f"  ✓ Removed {n} chunks for '{arg.strip()}'")

            elif cmd == "/new":
                session.reset()
                print("  Conversation cleared.")

            elif cmd == "/model":
                if not arg:
                    print(f"  Current model: {session.model}")
                else:
                    session.model = arg.strip()
                    print(f"  Switched to model: {session.model}")

            else:
                print(f"  Unknown command '{cmd}'. Type /help for help.")

        # ── Chat ──────────────────────────────────────────────────
        else:
            answer, sources = session.ask(user_input)
            print(f"\nDocuChat: {answer}")
            if sources:
                print("\n  Sources:")
                for src in sources:
                    print(f"    • {src}")
            print()


if __name__ == "__main__":
    main()
