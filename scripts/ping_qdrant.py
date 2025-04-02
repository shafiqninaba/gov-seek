"""Github Action script to ping Qdrant vector store to keep the free tier cloud instance alive."""

import os
import sys
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings


def ping_qdrant():
    """Ping Qdrant vector store to keep the free tier cloud instance alive."""
    try:
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
        return True
    except Exception as e:
        print(f"Error pinging Qdrant: {str(e)}")
        return False


if __name__ == "__main__":
    success = ping_qdrant()
    sys.exit(0 if success else 1)
