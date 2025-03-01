"""Script to populate the vector store with scraped data from the data pipeline."""

from loguru import logger
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from pathlib import Path


class VectorStore:
    """VectorStore class to populate the vector store with scraped data from the data pipeline."""

    def __init__(self):
        """Initialize VectorStore with OpenAI API key and Qdrant API key."""
        load_dotenv()

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        if not os.environ.get("QDRANT_URL"):
            raise ValueError("QDRANT_URL environment variable is not set")

        qdrant_url = os.environ.get("QDRANT_URL")

        # if path doesnt exist
        if not Path(qdrant_url).exists():
            logger.warning(
                f"Qdrant path does not exist, creating a new Qdrant instance at {qdrant_url}"
            )
            self.client = QdrantClient(path=qdrant_url)
            self.client.create_collection(
                collection_name="demo_collection",
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name="demo_collection",
                embedding=embeddings,
            )
            logger.info(f"Qdrant instance created at {qdrant_url}")
        else:
            self.vector_store = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                collection_name="demo_collection",
                path=qdrant_url,
            )
            logger.info(f"Qdrant instance found at {qdrant_url}")


if __name__ == "__main__":
    vector_store = VectorStore()
    logger.info("Vector store initialized")
