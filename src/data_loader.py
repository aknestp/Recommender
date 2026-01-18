# src/data_loader.py

import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def load_local_data(file_path: str) -> pd.DataFrame:
    """Memuat data dari file CSV lokal."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File tidak ditemukan di: {file_path}")
        raise FileNotFoundError(f"Pastikan '{file_path}' ada di struktur proyek.")
        
    try:
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8")
        return df
    except Exception as e:
        print("CSV LOAD ERROR:", e)
        return pd.DataFrame()

import pandas as pd
import os

def load_data():
    # cek apakah sedang dijalankan dari file atau notebook
    try:
        base_path = os.path.dirname(os.path.dirname(__file__))
    except NameError:
        # fallback untuk Jupyter / Notebook
        base_path = os.getcwd()

    file_path = os.path.join(base_path, "data", "product_data.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File CSV tidak ditemukan: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("CSV kosong, tidak bisa melanjutkan.")

    return df

df = load_data()


