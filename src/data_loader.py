def load_local_data(file_path: str) -> pd.DataFrame:
    """Memuat data dari file CSV lokal."""
    
    if not os.path.exists(file_path):
        logger.error(f"❌ File tidak ditemukan di: {file_path}")
        raise FileNotFoundError(f"Pastikan '{file_path}' ada di struktur proyek.")
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        return pd.DataFrame()
