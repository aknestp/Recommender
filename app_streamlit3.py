# app_streamlit.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
import time

# Import modul lokal dari folder src
try:
    from src.data_loader import load_local_data
    from src.preprocessing import clean_and_handle_missing_values
    from src.feature_engineering import create_features
    from src.modelling import build_hybrid_model, calculate_evaluation_metrics
    from src.integratedRecommender import IntegratedRecommender
    from src.evaluasiLlm import LLMTools, HybridEvaluation
    from src.rekom import CollaborativeFilteringRecommender
except ImportError:
    # Fallback dummy jika src belum lengkap (Hanya untuk guarding error)
    st.error("Pastikan modul 'src' tersedia.")

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Konfigurasi Global ---
DATA_FILE_PATH = 'data/product_data.csv'

# ==========================================
# 1. CSS STYLING & VISUAL UPGRADE
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
        /* IMPORT FONT INTER */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* BACKGROUND APLIKASI: Light Gray */
        .stApp {
            background-color: #f8f9fa;
        }

        /* HEADINGS */
        h1, h2, h3, h4, h5, h6 {
            color: #1E293B !important;
            font-weight: 800 !important;
        }

        /* CARD STYLE (Container Produk) */
        /* Mengubah container border=True menjadi kartu putih timbul */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        /* Hover Effect pada Card */
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
            border-color: #cbd5e1;
        }

        /* HEADER KHUSUS (Gradient Blue) */
        /* Container dengan ID marker khusus akan berubah jadi gradient */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Memaksa text di dalam Header Gradient menjadi Putih */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) * {
            color: white !important;
        }

        /* TOMBOL PRIMARY (Gradient Button) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(to right, #3b82f6, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            transform: scale(1.02);
        }
        
        /* TOMBOL SECONDARY/DEFAULT */
        div.stButton > button[kind="secondary"] {
            border: 1px solid #cbd5e1;
            border-radius: 8px;
        }

        /* INPUT SEARCH styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
        }

        /* UTILITY CLASSES */
        .product-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.4;
            height: 2.8em; 
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            margin-bottom: 0.5rem;
        }
        
        .metric-badge {
            background-color: #dbeafe;
            color: #1d4ed8;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* Styling untuk Kategori Card */
        .category-card-img {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 10px;
            position: relative;
            transition: transform 0.2s;
        }
        .category-card-img:hover {
            transform: scale(1.03);
        }
        .category-label {
            background: linear-gradient(to top, rgba(15, 23, 42, 0.9), transparent);
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
            position: absolute;
            bottom: 0;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Fungsi Bantu Logika ---

def add_to_cart(pid):
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if pid not in st.session_state.cart:
        st.session_state.cart.append(pid)
        st.toast(f"Produk berhasil ditambahkan ke keranjang! 🛒", icon="✅")
    else:
        st.toast(f"Produk sudah ada di keranjang!", icon="⚠️")

# ==========================================
# 2. KOMPONEN UI (MODERN STYLE)
# ==========================================

def display_evaluation_ui(evaluation: HybridEvaluation):
    """Menampilkan hasil evaluasi LLM dengan gaya modern (Colorful Score)."""
    score = evaluation.score
    
    # Warna dinamis berdasarkan skor
    if score >= 8:
        color, bg_color, icon = "#22c55e", "#dcfce7", "🌟 Excellent"
    elif score >= 5:
        color, bg_color, icon = "#f97316", "#ffedd5", "⚖️ Moderate"
    else:
        color, bg_color, icon = "#ef4444", "#fee2e2", "⚠️ Low Relevance"

    st.markdown("---")
    # Container Evaluasi
    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        with c1:
            st.markdown(f"""
                <div style="background-color: {bg_color}; border-radius: 12px; padding: 20px; text-align: center;">
                    <h1 style="color: {color} !important; margin: 0; font-size: 3rem;">{score}</h1>
                    <p style="color: {color}; font-weight: bold; margin: 0;">{icon}</p>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.subheader("🤖 Analisis AI")
            st.info(evaluation.description)
            with st.expander("Lihat Detail Alasan"):
                for r in evaluation.reasons:
                    st.markdown(f"- {r}")
                st.markdown(f"**Summary:** _{evaluation.summary}_")

# --- POP-UP DETAIL PRODUK (Dialog) ---
@st.dialog("Detail Produk Lengkap", width="large")
def show_product_popup(product_data, score=None):
    """Popup modern dengan layout Grid."""
    
    # Layout: Gambar Kiri, Info Kanan
    c_img, c_info = st.columns([1, 1.2], gap="medium")
    
    with c_img:
        img_url = str(product_data.get('ImageURL', '')).split('|')[0]
        if img_url and img_url != 'nan' and pd.notna(img_url):
            st.image(img_url, use_container_width=True)
        else:
            st.markdown('<div style="height:250px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:10px; color:#94a3b8;">No Image</div>', unsafe_allow_html=True)

    with c_info:
        st.caption(f"{product_data.get('Category', '-')} • {product_data.get('Brand', '-')}")
        st.markdown(f"## {product_data.get('Name', 'No Name')}")
        
        # Rating Stars
        rating_val = int(product_data.get('Rating', product_data.get('average_rating', 0)))
        stars = "★" * rating_val + "☆" * (5 - rating_val)
        st.markdown(f"<span style='color:#f59e0b; font-size:1.2rem;'>{stars}</span> <span style='color:#64748b; font-size:0.9rem;'>({product_data.get('ReviewCount', 0)} reviews)</span>", unsafe_allow_html=True)
        
        if score:
            st.markdown(f"<span class='metric-badge'>Relevance Score: {score:.4f}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.write(product_data.get('Description', 'Tidak ada deskripsi.'))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tombol Aksi
        col_cart, col_buy = st.columns(2)
        with col_cart:
            prod_id = product_data.get('ProdID', product_data.get('Name'))
            if st.button("🛒 Add to Cart", use_container_width=True, key=f"popup_cart_{prod_id}"):
                add_to_cart(prod_id)
        
        with col_buy:
            if st.button("🛍️ Buy Now", type="primary", use_container_width=True, key=f"popup_buy_{product_data.get('Name')}"):
                with st.spinner("Memproses pembayaran..."):
                    time.sleep(1.5)
                st.balloons()
                st.success("Pembayaran Berhasil! Terima kasih telah berbelanja.")

    st.markdown("---")
    
    # Spesifikasi (Grid Kecil)
    st.markdown("### Spesifikasi Teknis")
    exclude_cols = ['Name', 'Brand', 'Category', 'Rating', 'ReviewCount', 'Description', 'ImageURL', 'final_score', 'Name_norm', 'similarity', 'rating_norm', 'review_norm', 'average_rating']
    details = {k: v for k, v in product_data.items() if k not in exclude_cols and pd.notna(v) and str(v).strip() != ''}
    
    if details:
        cols_spec = st.columns(3)
        for i, (k, v) in enumerate(details.items()):
            with cols_spec[i % 3]:
                st.markdown(f"**{k}**")
                st.caption(str(v))

def render_product_card(row, full_df=None, prefix=""):
    """Merender kartu produk dengan desain 'Card' baru."""
    
    # Menggunakan container(border=True) yang sudah di-style CSS
    with st.container(border=True):
        # 1. Image Area (Fixed Ratio)
        img_url = str(row.get('ImageURL', '')).split('|')[0].strip() if pd.notna(row.get('ImageURL')) else None
        
        if img_url:
            st.markdown(f"""
                <div style="height: 150px; display: flex; justify-content: center; align-items: center; overflow: hidden; margin-bottom: 12px; border-radius: 8px;">
                    <img src="{img_url}" style="height: 100%; width: 100%; object-fit: contain;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="height: 150px; background-color: #f1f5f9; display: flex; justify-content: center; align-items: center; margin-bottom: 12px; border-radius: 8px; color: #94a3b8;">
                    📷 No Image
                </div>
            """, unsafe_allow_html=True)

        # 2. Content
        st.markdown(f"<div class='product-title' title='{row.get('Name', 'No Name')}'>{row.get('Name', 'No Name')}</div>", unsafe_allow_html=True)
        
        # Meta Info
        c_brand, c_rate = st.columns([2, 1])
        with c_brand:
            st.caption(row.get('Brand', '-'))
        with c_rate:
            rating_int = int(row.get('Rating', row.get('average_rating', 0)))
            st.markdown(f"⭐ **{rating_int}**")

        # Score Badge (jika ada)
        if 'final_score' in row:
             st.markdown(f"<div style='margin-bottom:8px;'><span class='metric-badge'>Score: {row['final_score']:.2f}</span></div>", unsafe_allow_html=True)
        else:
             st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 3. Action Button
        unique_key = f"{prefix}_btn_{row.get('ProdID', row.name)}" if prefix else f"btn_{row.get('ProdID', row.name)}"
        
        if st.button("Lihat Detail", key=unique_key, use_container_width=True):
            if full_df is not None and row.name in full_df.index:
                full_data = full_df.loc[row.name]
            else:
                full_data = row
            score_val = row.get('final_score', None)
            show_product_popup(full_data, score=score_val)

def display_grid(products, title, full_df=None, prefix=""):
    """Menampilkan grid produk responsive."""
    st.subheader(title)
    cols = st.columns(5)
    for idx, (_, product) in enumerate(products.iterrows()):
        with cols[idx % 5]:
            render_product_card(product, full_df=full_df, prefix=prefix)

# --- INITIALIZATION ---
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
        recommender = IntegratedRecommender(df, hybrid_sim)
        cf_recommender = CollaborativeFilteringRecommender(data_path=DATA_FILE_PATH, num_users=500, random_seed=42)
        
        return df, recommender, llm_tools, metrics, cf_recommender
        
    except Exception as e:
        logger.error(f"Error initialization: {e}")
        return None, None, None, None, None

# ==========================================
# 3. HALAMAN (PAGES)
# ==========================================

def page_recommender(df, recommender, llm_tools, metrics, cf_recommender):
    # --- HEADER SEARCH (Gradient Style) ---
    with st.container(border=True):
        st.markdown('<span id="header-marker"></span>', unsafe_allow_html=True) # Marker untuk CSS Gradient
        
        c_back, c_logo, c_search, c_num, c_actions = st.columns([0.5, 1.2, 3.5, 0.8, 2], gap="small")
        
        with c_back:
            if st.button("⬅️", help="Home", use_container_width=True):
                st.session_state["current_page"] = "home"
                st.rerun()

        with c_logo:
             st.markdown("<h3 style='color:white !important; margin:0;'>clickmart</h3>", unsafe_allow_html=True)

        with c_search:
            default_query = st.session_state.get("global_search_query", "")
            product_query = st.text_input("Search", value=default_query, placeholder="Cari produk...", label_visibility="collapsed")
            
        with c_num:
            top_n = st.number_input("Jml", 5, 50, 10, 5, label_visibility="collapsed")

        with c_actions:
            ac1, ac2 = st.columns(2)
            with ac1:
                run_search = st.button("🔍 Cari", type="primary", use_container_width=True)
            with ac2:
                has_recs = 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None
                run_eval = st.button("✨ AI Eval", disabled=not has_recs, use_container_width=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Info Sistem")
        st.info(f"Total SKU: {len(df)}")
        if st.button("🔄 Refresh System"):
            st.cache_resource.clear()
            st.rerun()
            
        st.markdown("---")
        st.header("🛒 Keranjang")
        if 'cart' in st.session_state and st.session_state.cart:
            st.success(f"Items: {len(st.session_state.cart)}")
            if st.button("Checkout / Kosongkan"):
                st.session_state.cart = []
                st.toast("Checkout berhasil!", icon="💳")
                st.rerun()
        else:
            st.caption("Keranjang kosong.")

    # --- LOGIKA PENCARIAN ---
    trigger_home = default_query and st.session_state.get("trigger_search", False)
    
    if (run_search or trigger_home) and product_query:
        st.session_state.trigger_search = False 
        
        with st.spinner(f"🔍 Mencari produk terbaik untuk '{product_query}'..."):
            interpreted = product_query
            if llm_tools:
                interpreted = llm_tools.interpret_query_with_llm(product_query)
            
            if interpreted != product_query:
                st.toast(f"AI: Query diperjelas menjadi '{interpreted}'", icon="💡")

            recs = recommender.get_recommendations(interpreted, int(top_n))

            if isinstance(recs, str) or recs.empty:
                st.error("Tidak ada produk ditemukan.")
                st.session_state['current_rekom'] = None
            else:
                st.session_state['current_rekom'] = recs
                if 'last_eval_result' in st.session_state:
                    del st.session_state['last_eval_result']
        st.rerun()

    # --- LOGIKA EVALUASI ---
    if run_eval and 'current_rekom' in st.session_state:
        if llm_tools:
            with st.spinner("🤖 Gemini sedang menganalisis hasil rekomendasi..."):
                eval_res = llm_tools.evaluate_recommendation_with_llm(st.session_state['current_rekom'])
                if eval_res:
                    st.session_state['last_eval_result'] = eval_res

    # --- DISPLAY HASIL ---
    st.markdown("<br>", unsafe_allow_html=True)

    if 'last_eval_result' in st.session_state:
        display_evaluation_ui(st.session_state['last_eval_result'])

    if 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None:
        recs = st.session_state['current_rekom']
        display_grid(recs, f"Hasil Pencarian ({len(recs)} Produk)", full_df=df, prefix="search")

    # --- FOOTER EDA ---
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.expander("📊 Data Analytics Dashboard"):
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Distribusi Rating")
            fig1, ax1 = plt.subplots(figsize=(6, 3))
            sns.histplot(df['Rating'], bins=10, kde=True, ax=ax1, color='#3b82f6')
            ax1.set_frame_on(False)
            st.pyplot(fig1)
        with c2:
            st.caption("Kategori Terpopuler")
            st.bar_chart(df['Category'].value_counts().head(10), color='#3b82f6')

def page_home(df, cf_recommender):
    # --- HERO SECTION (Gradient Blue) ---
    with st.container(border=True):
        st.markdown('<span id="header-marker"></span>', unsafe_allow_html=True) # Marker CSS
        
        col_text, col_img = st.columns([2, 1])
        with col_text:
            st.markdown("# 👋 Selamat Datang di clickmart")
            st.markdown("Temukan produk skincare & kosmetik terbaik dengan **AI Recommendation**.")
            
            # Search Bar Besar
            search_input = st.text_input("Search Hero", placeholder="Apa yang sedang kamu cari hari ini?", label_visibility="collapsed")
            
            if st.button("Mulai Pencarian 🚀", type="primary"):
                if search_input:
                    st.session_state["global_search_query"] = search_input
                    st.session_state["trigger_search"] = True
                    st.session_state["current_page"] = "recommender"
                    st.rerun()
                else:
                    st.toast("Ketik sesuatu dulu ya!", icon="😅")
                    
        with col_img:
            # Placeholder illustrasi (bisa diganti gambar real)
            st.markdown("""
                <div style="display:flex; justify-content:center; align-items:center; height:100%; font-size: 5rem;">
                🛍️✨
                </div>
            """, unsafe_allow_html=True)

    # --- Categories ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🛍️ Kategori Pilihan")
    
    categories = [
        {"name": "Skincare", "image": "https://i.pinimg.com/736x/4c/16/7c/4c167c5ac422efd13eba8e07d04274a7.jpg"},
        {"name": "Bodycare", "image": "https://i.pinimg.com/736x/bf/00/df/bf00df3d3cf4271cdb625a387936f90d.jpg"},
        {"name": "Haircare", "image": "https://i.pinimg.com/736x/02/d5/7f/02d57f094a70a0b5c6c1f7279b21a2d3.jpg"},
        {"name": "Make Up", "image": "https://i.pinimg.com/1200x/e4/14/34/e414342a7464892f646fe9baeee41c51.jpg"},
        {"name": "Others", "image": "https://i.pinimg.com/736x/2d/f3/c2/2df3c287f50c35de6d65d16ff225ebda.jpg"}
    ]

    cols = st.columns(5)
    for i, (col, category) in enumerate(zip(cols, categories)):
        with col:
            # Menggunakan teknik container click hack (tombol invisible di atas gambar)
            with st.container():
                if st.button("⠀", key=f"cat_btn_{i}", use_container_width=True):
                    st.toast(f"Kategori {category['name']} dipilih! (Coming Soon)", icon="🚧")
                
                st.markdown(f"""
                <div class="category-card-img">
                    <img src="{category['image']}" style="width: 100%; height: 100px; object-fit: cover;">
                    <div class="category-label">{category['name']}</div>
                </div>
                
                <style>
                /* Tombol Invisible agar gambar bisa diklik */
                div[data-testid="column"] button {{
                    position: absolute !important;
                    z-index: 2 !important;
                    opacity: 0 !important;
                    height: 120px !important;
                    margin-top: 0px !important;
                }}
                </style>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Best Sellers (Logic CF) ---
    if cf_recommender:
        most_liked = cf_recommender.get_most_liked_products(top_n=5)
        if not most_liked.empty:
            display_grid(most_liked, "🔥 Produk Terlaris (Best Seller)", full_df=df, prefix="best")

    # --- Featured ---
    st.subheader("✨ Produk Unggulan Kami")
    display_df = df[df['ImageURL'].notna() & (df['ImageURL'] != '')].head(10)
    
    # Render menggunakan loop manual agar bisa pakai grid system
    cols_feat = st.columns(5)
    for idx, (index, row) in enumerate(display_df.iterrows()):
        with cols_feat[idx % 5]:
            render_product_card(row, full_df=df, prefix="feat")

    # --- Recommendations (CF) ---
    if cf_recommender:
        st.markdown("<br>", unsafe_allow_html=True)
        recom_prods = cf_recommender.get_most_liked_products(top_n=10) # Contoh logic CF sederhana
        if not recom_prods.empty:
            display_grid(recom_prods, "❤️ Rekomendasi Untuk Anda", full_df=df, prefix="recom")

    # FOOTER
    st.markdown("""
        <br><br>
        <div style='background-color: #0f172a; color: #94a3b8; padding: 30px; text-align: center; border-radius: 12px;'>
            <h4 style='color:white !important;'>clickmart AI</h4>
            <p style='font-size: 0.9rem; margin:0;'>Smart Shopping Experience Powered by Gemini LLM & Collaborative Filtering</p>
            <p style='font-size: 0.8rem; margin-top:10px;'>Developed by Kelompok 5 DSAI CAMP3</p>
        </div>
    """, unsafe_allow_html=True)

# --- Main Controller ---

def main():
    st.set_page_config(page_title="clickmart", page_icon="🛍️", layout="wide")

    # 1. Inject Style Modern
    inject_custom_css()

    # 2. State Management
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    # 3. Initialize
    df, recommender, llm_tools, metrics, cf_recommender = initialize_system()

    if df is None:
        st.error("Gagal memuat data. Pastikan file CSV tersedia.")
        return

    # 4. Routing
    if st.session_state["current_page"] == "home":
        page_home(df, cf_recommender)
    elif st.session_state["current_page"] == "recommender":
        page_recommender(df, recommender, llm_tools, metrics, cf_recommender)

if __name__ == "__main__":
    main()