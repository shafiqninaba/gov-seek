"""This script combines the input data and the generated embeddings into a single dataframe and saves it as a parquet file."""

from pathlib import Path
import pandas as pd

if __name__ == "__main__":
    dataframes = []
    for file in Path("/workspaces/codespaces-blank/data/scraped_data").rglob("*.json"):
        jsonObj = pd.read_json(path_or_buf=file)
        dataframes.append(jsonObj)

    input_files_df = pd.concat(dataframes, ignore_index=True)

    dataframes = []
    for file in Path("/workspaces/codespaces-blank/data/generated_embeddings").rglob(
        "*.jsonl"
    ):
        jsonObj = pd.read_json(path_or_buf=file, lines=True)
        jsonObj["embedding"] = jsonObj["response"].apply(
            lambda x: x["body"]["data"][0]["embedding"]
        )
        jsonObj.drop(columns=["response", "error", "id"], inplace=True)
        dataframes.append(jsonObj)

    output_files_df = pd.concat(dataframes, ignore_index=True)

    # merge input_files_df and output_files_df on uuid and custom_id. keep uuid
    merged_df = pd.merge(
        input_files_df,
        output_files_df,
        how="inner",
        left_on="uuid",
        right_on="custom_id",
    )
    merged_df.drop(columns=["custom_id"], inplace=True)

    merged_df.to_parquet(
        "/workspaces/codespaces-blank/data/generated_embeddings/combined_embeddings.parquet"
    )
