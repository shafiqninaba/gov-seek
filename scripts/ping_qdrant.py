"""Github Action script to ping Qdrant vector store to keep the free tier cloud instance alive."""

import os
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings


def ping_qdrant():
    """Ping Qdrant vector store to keep the free tier cloud instance alive."""
    embeddings = OpenAIEmbeddings()

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name="demo_collection",
        url=os.environ.get("QDRANT_URL"),
        api_key=os.environ.get("QDRANT_API_KEY"),
    )

    # Perform a simple query
    vector_store.similarity_search("ping test", k=1)
    print("Successfully pinged Qdrant vector store")


if __name__ == "__main__":
    ping_qdrant()
