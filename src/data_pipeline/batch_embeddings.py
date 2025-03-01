"Script to batch upload data to OpenAI API to generate embeddings"

from loguru import logger
from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path
import json
from tqdm import tqdm
import tiktoken


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text.

    Args:
        text: Input text

    Returns:
        Number of tokens
    """
    encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def combine_jsonl_files(data_dir: str, output_file: str):
    """Combine multiple JSON files into a single JSONL file.

    Args:
        data_dir: Directory containing JSON files
        output_file: Output JSONL file
    """
    file_counter = 0
    total_tokens = 0

    json_files = list(Path(data_dir).rglob("*.json"))

    for scraped_json_file in tqdm(json_files, desc="Processing files"):
        # load the contents of the file
        with open(scraped_json_file) as f:
            d = json.load(f)

            for item in tqdm(
                d, desc=f"Processing items in {scraped_json_file.name}", leave=False
            ):
                # calculate the number of tokens in the text
                tokens = count_tokens(item["text"])
                total_tokens += tokens

                # if the total number of tokens exceeds 3000000, increment file counter and write to a new file
                if total_tokens > 3000000:
                    file_counter += 1
                    total_tokens = tokens
                # write the item to the output file
                with open(
                    output_file.replace(".jsonl", f"_{file_counter}.jsonl"), "a"
                ) as f:
                    line = {
                        "custom_id": item["uuid"],
                        "method": "POST",
                        "url": "/v1/embeddings",
                        "body": {
                            "model": "text-embedding-3-small",
                            "input": item["text"],
                            "encoding_format": "float",
                        },
                    }
                    f.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    combined_json_file = "data/batch_jobs/batchinput.jsonl"
    combine_jsonl_files("data/scraped_data", combined_json_file)

    client = OpenAI()

    for file in Path("data/batch_jobs").rglob("*.jsonl"):
        batch_input_file = client.files.create(file=open(file, "rb"), purpose="batch")

        logger.info(f"Batch input file created: {batch_input_file.id}")

        batch_input_file_id = batch_input_file.id
        batch_metadata = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/embeddings",
            completion_window="24h",
            metadata={"description": f"scraped data batch embeddings: {file.name}"},
        )

        logger.info(f"{batch_input_file_id} batch uploaded to OpenAI API")
        logger.info(f"Batch metadata: {batch_metadata}")
