# app_streamlit.py

import streamlit as st
import logging
from src.data_loader import load_local_data
from src.preprocessing import clean_and_handle_missing_values
from src.feature_engineering import create_features
from src.modelling import build_hybrid_model, calculate_evaluation_metrics
from src.integratedRecommender import IntegratedRecommender
from src.evaluasiLlm import LLMTools
from src.rekom import CollaborativeFilteringRecommender

# Import UI Components & Views
from components.layout import inject_custom_css, ICON_PATH, DATA_FILE_PATH
from views import home, recommender, category

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Inisialisasi System ---
@st.cache_resource
def initialize_system():
    try:
        df = load_local_data(DATA_FILE_PATH)
        if df.empty: return None, None, None, None, None

        df = clean_and_handle_missing_values(df)
        df, tfidf_matrix = create_features(df)
        hybrid_sim = build_hybrid_model(df, tfidf_matrix)
        metrics = calculate_evaluation_metrics(df, hybrid_sim)
        llm_tools = LLMTools()
        recommender_system = IntegratedRecommender(df, hybrid_sim)
        cf_recommender = CollaborativeFilteringRecommender(data_path=DATA_FILE_PATH, num_users=500, random_seed=42)
        
        return df, recommender_system, llm_tools, metrics, cf_recommender
    except Exception as e:
        logger.error(f"Error initalization: {e}")
        return None, None, None, None, None

def main():
    st.set_page_config(page_title="clickmart", page_icon=ICON_PATH, layout="wide")

    if 'current_page' not in st.session_state:
        st.session_state["current_page"] = "home"
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

    inject_custom_css(st.session_state.dark_mode)

    df, recommender_sys, llm_tools, metrics, cf_recommender = initialize_system()

    if df is None:
        st.error("Data tidak ditemukan. Pastikan file CSV tersedia.")
        return

    # Routing
    if st.session_state["current_page"] == "home":
        home.show(df, cf_recommender)
        
    elif st.session_state["current_page"] == "recommender":
        recommender.show(df, recommender_sys, llm_tools, metrics, cf_recommender)
        
    elif st.session_state["current_page"] == "category_view":
        category.show(df)

if __name__ == "__main__":
    main()
