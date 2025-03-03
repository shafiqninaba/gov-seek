"""Script to populate the vector store with scraped data from the data pipeline."""

from loguru import logger
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import pandas as pd
from tqdm import tqdm


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
        self.client = QdrantClient(url=qdrant_url)

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

    def populate_vector_store_from_parquet(self, parquet_path: str):
        """Populate the vector store from a parquet file."""

        df = pd.read_parquet(parquet_path)

        logger.info(f"Populating vector store with {len(df)} rows")

        for _, row in tqdm(
            df.iterrows(), total=len(df), desc="Populating vector store"
        ):
            self.client.upsert(
                collection_name="demo_collection",
                points=[
                    PointStruct(
                        id=str(row["uuid"]),
                        vector=row["embedding"],
                        payload={
                            "metadata": {"source": row["link"]},
                            "page_content": row["text"],
                        },
                    )
                ],
            )


if __name__ == "__main__":
    vector_store = VectorStore()
    logger.info("Vector store initialized")

    vector_store.populate_vector_store_from_parquet(
        "/workspaces/codespaces-blank/data/generated_embeddings/combined_embeddings.parquet"
    )
    logger.info("Vector store populated with scraped data")
