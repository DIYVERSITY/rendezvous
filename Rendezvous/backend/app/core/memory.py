import chromadb
from sentence_transformers import SentenceTransformer

class MemoryManager:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="conversation_memory")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def add_message(self, session_id: str, message: str):
        embedding = self.model.encode(message).tolist()
        self.collection.add(
            embeddings=[embedding],
            documents=[message],
            metadatas=[{"session_id": session_id}],
            ids=[str(self.collection.count() + 1)]
        )

    def query(self, session_id: str, query_text: str, n_results: int = 2):
        query_embedding = self.model.encode(query_text).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"session_id": session_id}
        )
        return results['documents'][0]

memory_manager = MemoryManager()
