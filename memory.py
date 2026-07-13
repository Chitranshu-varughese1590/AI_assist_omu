"""
memory.py — Omu's long-term memory.

Stores every user message + Omu's reply in a local vector database (ChromaDB)
so that future queries can retrieve relevant past context.

Everything here runs 100% locally and free — no cloud account needed.
"""

import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import time


class Memory:
    def __init__(self, db_path="./omu_memory_db", collection_name="omu_memory"):
        # Persistent local database — saved to disk in db_path, survives restarts
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

        # Small, fast, free local embedding model (downloads once, ~80MB)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add_memory(self, user_text, assistant_text):
        """Save one exchange (user message + Omu's reply) into memory."""
        combined = f"User: {user_text}\nOmu: {assistant_text}"
        embedding = self.embedder.encode(combined).tolist()

        self.collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding],
            documents=[combined],
            metadatas=[{"timestamp": time.time()}],
        )

    def recall(self, query, n_results=3):
        """
        Given a new query, find the most relevant past exchanges.
        Returns a list of strings (past conversation snippets).
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
        )

        # results["documents"] is a list of lists (one per query) — we only sent 1 query
        return results["documents"][0] if results["documents"] else []
