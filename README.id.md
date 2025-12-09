# Rekomender Hibrid untuk E‑commerce (FP_DSAI)

Sistem rekomendasi hibrid sederhana yang menggabungkan pendekatan content-based dan collaborative filtering untuk rekomendasi produk. Repositori ini berisi demo aplikasi Streamlit, kode preprocessing dan pemodelan, serta komponen collaborative filtering sederhana untuk eksperimen dan keperluan pembelajaran.

**Sorotan**
- Rekomender hibrid yang menggabungkan kesamaan teks, rating, dan jumlah ulasan.
- UI interaktif menggunakan Streamlit (`app_streamlit.py`).
- Notebook dan skrip untuk pengembangan model dan eksperimen (`colabGoogle/Hybrid_Model.ipynb`).
- Collaborative filtering yang disimulasikan untuk tujuan demo.

Badge
- Build/CI: `status: unknown` (tambahkan badge CI Anda di sini)
- PyPI: `version: n/a`
- Lisensi: Tidak ada (tambahkan file `LICENSE` jika diperlukan)

Mengapa proyek ini berguna
- Menunjukkan cara menggabungkan fitur TF‑IDF / konten dengan sinyal berbasis rating untuk menghasilkan peringkat rekomendasi akhir.
- Mencakup pipeline end-to-end: pemuatan data, pembersihan, rekayasa fitur, pemodelan hibrid, dan UI interaktif.
- Cocok untuk materi pengajaran, demo, atau sebagai basis pengembangan lebih lanjut.

Struktur proyek
- `app_streamlit.py` — Titik masuk aplikasi Streamlit (demo UI).
- `data/product_data.csv` — Dataset produk contoh yang digunakan oleh aplikasi.
- `colabGoogle/Hybrid_Model.ipynb` — Notebook Jupyter dengan eksperimen dan walkthrough.
- `src/` — Modul inti (data loader, preprocessing, feature engineering, modelling, recommenders).
- `components/`, `views/` — Komponen UI dan halaman yang digunakan oleh aplikasi Streamlit.

Panduan cepat

1. Buat environment Python 3.10+ dan pasang dependensi:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows (bash)
pip install -r requirements.txt
```

2. Jalankan aplikasi demo Streamlit:

```bash
streamlit run app_streamlit.py
```

3. Buka notebook untuk eksplorasi model:

```bash
# Buka dengan Jupyter atau di Colab: colabGoogle/Hybrid_Model.ipynb
```

Data
- Dataset default: `data/product_data.csv` — aplikasi Streamlit dan recommender membaca file ini secara default. Ganti dengan dataset Anda yang memiliki kolom yang diharapkan (kolom umum yang digunakan: `ProdID`, `Name`, `Brand`, `Category`, `Rating`, `ReviewCount`, `ImageURL`, `Description`, `Tags`).

Contoh pemakaian (Python)

Menjalankan recommender hibrid secara programatik:

```python
from src.integratedRecommender import IntegratedRecommender
from src.data_loader import load_local_data

df = load_local_data('data/product_data.csv')
# bangun atau muat matriks similarity menggunakan utilitas di `src/modelling.py`
# diasumsikan `hybrid_sim` sudah tersedia
recommender = IntegratedRecommender(df, hybrid_sim)
print(recommender.get_recommendations('nama produk contoh', n=5))
```

UI Streamlit
- Aplikasi Streamlit menggunakan komponen di `components/` dan halaman di `views/`. Gunakan UI untuk: menjelajah produk, melihat halaman kategori, dan meminta rekomendasi.

Catatan pengembang
- Modul utama:
  - `src/data_loader.py` — helper pemuatan data
  - `src/preprocessing.py` — pembersihan dan penanganan nilai hilang
  - `src/feature_engineering.py` — TF‑IDF dan pembuatan fitur
  - `src/modelling.py` — pembuatan matriks similarity hibrid dan metrik evaluasi
  - `src/integratedRecommender.py` — peranking rekomendasi hibrid utama
  - `src/rekom.py` — recommender collaborative-filtering yang disimulasikan (menghasilkan interaksi dan membangun similarity item)

- Dependensi: lihat `requirements.txt`. Paket penting termasuk `pandas`, `scikit-learn`, `streamlit`, dan `langchain-core` (digunakan untuk utilitas LLM di `src/evaluasiLlm.py`).

Kontribusi
- Kontribusi dipersilakan: buka issue untuk diskusi fitur atau bug. Untuk perubahan kode, silakan buat pull request dengan deskripsi jelas dan tes/contoh bila relevan.
- Anda juga bisa menambahkan `CONTRIBUTING.md` di root repositori untuk panduan kontributor.

Dukungan
- Untuk masalah, gunakan tab Issues di repositori. Untuk bantuan mendesak, hubungi maintainer di bawah.

Maintainer
- Pemilik repositori: `umamhaniff` (GitHub: umamhaniff)

Lisensi
- Tidak ditemukan file `LICENSE` di repositori ini. Tambahkan file `LICENSE` jika Anda ingin menetapkan lisensi.

Langkah berikutnya dan saran
- Tambahkan `CONTRIBUTING.md` untuk mendokumentasikan alur kontribusi.
- Tambahkan unit test dan CI untuk memvalidasi alur dasar (`app_streamlit.py` imports, fungsi `src/`).
- Ganti badge placeholder dengan badge CI dan paket yang aktual.

---