# src/data_loader.py

import pandas as pd
import streamlit as st
import logging
import os

logger = logging.getLogger(__name__)

def load_local_data(file_path: str) -> pd.DataFrame:
    """Memuat data dari file CSV lokal."""
    
    if not os.path.exists(file_path):
        logger.error(f"❌ File tidak ditemukan di: {file_path}")
        raise FileNotFoundError(f"Pastikan '{file_path}' ada di struktur proyek.")
    
    # Debug untuk Streamlit Cloud
    st.write("CWD:", os.getcwd())
    st.write("Files in CWD:", os.listdir(os.getcwd()))
    st.write("Files in data:", os.listdir(os.path.join(os.getcwd(), "data")))
    
    try:
        df = pd.read_csv(file_path)
        st.write("CSV loaded! Shape:", df.shape)
        return df
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        return pd.DataFrame()
