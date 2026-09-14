import chromadb
from sentence_transformers import SentenceTransformer
from app.config import CHROMA_DIR, EMBEDDING_MODEL

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
embedder = SentenceTransformer(EMBEDDING_MODEL)


def _collection_name(project_id: str) -> str:
    # One Chroma collection per Project = retrieval can never cross Project boundaries.
    return f"project_{project_id}"


def add_chunks(project_id: str, material_id: str, material_name: str, chunks: list[dict]):
    collection = chroma_client.get_or_create_collection(_collection_name(project_id))

    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts).tolist()
    ids = [f"{material_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"material_id": material_id, "material_name": material_name, "page": c["page"]}
        for c in chunks
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def search(project_id: str, query: str, top_k: int = 4) -> list[dict]:
    collection = chroma_client.get_or_create_collection(_collection_name(project_id))
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    hits = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            hits.append({"text": doc, "material_name": meta["material_name"], "page": meta["page"], "distance": dist})
    return hits