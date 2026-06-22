import os
import pandas as pd


DATASET_FOLDER = "uploads"


def save_dataframe(file, dataset_id):

    ext = file.name.split(".")[-1]
    # ensure uploads folder exists
    os.makedirs(DATASET_FOLDER, exist_ok=True)

    path = f"{DATASET_FOLDER}/{dataset_id}.{ext}"

    with open(path, "wb") as f:
        f.write(file.getbuffer())


def load_dataframe(dataset_id):

    csv_path = f"{DATASET_FOLDER}/{dataset_id}.csv"
    xlsx_path = f"{DATASET_FOLDER}/{dataset_id}.xlsx"

    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    if os.path.exists(xlsx_path):
        return pd.read_excel(xlsx_path)

    raise FileNotFoundError("Dataset not found")