# Hybrid Recommender for E‑commerce (FP_DSAI)

-- Bahasa: English — For Bahasa Indonesia, see `README.id.md` --

A compact hybrid recommendation system combining content-based and collaborative filtering approaches for product recommendations. This repository includes a Streamlit demo app, preprocessing and modelling code, and a simple simulated collaborative filtering component for experimentation and teaching.

**Highlights**
- Hybrid recommender combining textual similarity, ratings, and review counts.
- Streamlit UI for interactive exploration (`app_streamlit.py`).
- Notebook and scripts for model development and experiments (`colabGoogle/Hybrid_Model.ipynb`).
- Lightweight simulated collaborative filtering for demo purposes.

Badges
- Build/CI: `status: unknown` (add your CI badge here)
- PyPI: `version: n/a`
- License: Not included (add `LICENSE` if needed)

**Why this project is useful**
- Demonstrates how to combine TF-IDF / content features with rating-based signals to produce a final ranked recommendation.
- Contains a full end-to-end pipeline: data loading, preprocessing, feature engineering, hybrid modelling, and an interactive UI.
- Useful as a teaching/demo project or a base for extending into production-ready recommenders.

Contents
- `app_streamlit.py` — Streamlit application entry point (demo UI).
- `data/product_data.csv` — Sample product dataset used by the app.
- `colabGoogle/Hybrid_Model.ipynb` — Jupyter notebook with experiments and walkthrough.
- `src/` — Core modules (data loader, preprocessing, feature engineering, modelling, recommenders).
- `components/`, `views/` — UI components and page views used by the Streamlit app.

Quick start

1. Create a Python 3.10+ virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows (bash)
pip install -r requirements.txt
```

2. Launch the Streamlit demo app:

```bash
streamlit run app_streamlit.py
```

3. Open the notebook for model exploration:

```bash
# Open with Jupyter or in Colab: colabGoogle/Hybrid_Model.ipynb
```

Data
- Default dataset: `data/product_data.csv` — the Streamlit app and recommenders read this file by default. Replace it with your dataset matching the expected columns (common columns used by code: `ProdID`, `Name`, `Brand`, `Category`, `Rating`, `ReviewCount`, `ImageURL`, `Description`, `Tags`).

Usage examples (Python)

Run the hybrid recommender programmatically:

```python
from src.integratedRecommender import IntegratedRecommender
from src.data_loader import load_local_data

df = load_local_data('data/product_data.csv')
# build or load a similarity matrix using modelling utilities in `src/modelling.py`
# here we assume `hybrid_sim` is available
recommender = IntegratedRecommender(df, hybrid_sim)
print(recommender.get_recommendations('example product name', n=5))
```

Streamlit UI
- The Streamlit app uses components in `components/` and pages in `views/`. Use the UI to: browse products, view category pages, and request recommendations.

Developer notes
- Key modules:
  - `src/data_loader.py` — data loading helpers
  - `src/preprocessing.py` — cleaning and missing-value handling
  - `src/feature_engineering.py` — TF-IDF and feature creation
  - `src/modelling.py` — build hybrid similarity matrix and evaluation metrics
  - `src/integratedRecommender.py` — main hybrid recommendation ranking
  - `src/rekom.py` — a simulated collaborative-filtering recommender (generates interactions and builds item similarity)

- Dependencies: See `requirements.txt`. Important packages include `pandas`, `scikit-learn`, `streamlit`, and `langchain-core` (used for LLM utilities in `src/evaluasiLlm.py`).

Contributing
- Contributions are welcome: open an issue to discuss feature requests or bug reports. For code changes, please submit a pull request with a clear description and tests/examples if applicable.
- Optionally add a `CONTRIBUTING.md` in the repository root with project-specific guidelines.

Support
- For issues, use the repository Issues tab. For urgent help, contact the maintainer listed below.

Maintainers
- Repository owner: `umamhaniff` (GitHub: umamhaniff)

License
- No LICENSE file found in this repository. Add a `LICENSE` file if you want to make the license explicit.

Next steps and suggestions
- Add a `CONTRIBUTING.md` to document contribution flow.
- Add unit tests and CI to validate basic flows (`app_streamlit.py` imports, `src/` functions).
- Replace placeholder badges with real CI and package badges.

---
