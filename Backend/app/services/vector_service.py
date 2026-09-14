import chromadb
from chromadb.utils import embedding_functions
from app.config import CHROMA_DIR

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
# Same all-MiniLM-L6-v2 model as sentence-transformers, but served over ONNX
# Runtime instead of full PyTorch — a fraction of the memory footprint, which
# matters on memory-constrained free-tier hosts. Model weights are fetched
# lazily on first call, not at import time.
embedder = embedding_functions.ONNXMiniLM_L6_V2()


def _collection_name(project_id: str) -> str:
    # One Chroma collection per Project = retrieval can never cross Project boundaries.
    return f"project_{project_id}"


def add_chunks(project_id: str, material_id: str, material_name: str, chunks: list[dict]):
    collection = chroma_client.get_or_create_collection(_collection_name(project_id))

    texts = [c["text"] for c in chunks]
    embeddings = [e.tolist() for e in embedder(texts)]
    ids = [f"{material_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"material_id": material_id, "material_name": material_name, "page": c["page"]}
        for c in chunks
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def search(project_id: str, query: str, top_k: int = 4) -> list[dict]:
    collection = chroma_client.get_or_create_collection(_collection_name(project_id))
    query_embedding = [e.tolist() for e in embedder([query])]

    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    hits = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            hits.append({"text": doc, "material_name": meta["material_name"], "page": meta["page"], "distance": dist})
    return hits