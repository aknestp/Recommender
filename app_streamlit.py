# app_streamlit.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
import time
import re

# Import modul lokal (Menggunakan struktur import Code 1)
from src.data_loader import load_local_data
from src.preprocessing import clean_and_handle_missing_values
from src.feature_engineering import create_features
from src.modelling import build_hybrid_model, calculate_evaluation_metrics
from src.integratedRecommender import IntegratedRecommender
from src.evaluasiLlm import LLMTools, HybridEvaluation
from src.rekom import CollaborativeFilteringRecommender

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Konfigurasi Global ---
DATA_FILE_PATH = 'data/product_data.csv'
LOGO_PATH = 'assets/logo.png' # Pastikan kamu punya file ini di folder assets
ICON_PATH = 'assets/icon2.png' # Opsional untuk icon tab

# Inisialisasi Session State untuk Dark Mode jika belum ada
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# ==========================================
# 1. CSS STYLING (Blue & White Theme)
# ==========================================
def inject_custom_css():
    # Tentukan palet warna Biru & Putih
    if st.session_state.dark_mode:
        # DARK MODE: Deep Navy Blue
        bg_color = "#0f172a"        # Slate 900 (Biru Dongker Gelap)
        text_color = "#f1f5f9"      # Slate 100 (Putih Tulang)
        card_bg = "#1e293b"         # Slate 800 (Biru Dongker Sedang)
        border_color = "#334155"    # Slate 700
        input_bg = "#1e293b"        
        # Header Gradient untuk Dark Mode
        header_grad = "linear-gradient(135deg, #020617 0%, #1e3a8a 100%)" 
    else:
        # LIGHT MODE: Clean White & Ice Blue
        bg_color = "#ffffff"        
        text_color = "#1e3a8a"      # Blue 900 (Biru Tua/Navy untuk Text)
        card_bg = "#ffffff"         # Putih Bersih
        border_color = "#bfdbfe"    # Blue 200 (Biru Muda Halus)
        input_bg = "#ffffff"
        # Header Gradient untuk Light Mode
        header_grad = "linear-gradient(135deg, #2563eb 0%, #60a5fa 100%)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        /* 1. Global App Style */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {text_color};
        }}
        
        .stApp {{
            background-color: {bg_color};
        }}

        .block-container {{
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
        }}
        
        /* 2. Typography Colors */
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: {text_color};
        }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: {text_color} !important;
        }}

        /* 3. Card Style (Custom) */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1); /* Shadow Biru Halus */
            padding: 1rem;
        }}
        
        /* 4. Header Gradient (Warna Biru) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) {{
            background: {header_grad};
            border: none;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) * {{
            color: white !important;
        }}

        /* 5. Input Fields */
        div[data-baseweb="input"] > div {{
            background-color: {input_bg} !important;
            border-color: {border_color} !important;
            color: {text_color} !important;
        }}
        input[class*="st-"] {{
            color: {text_color} !important;
        }}
        
        /* 6. Buttons (Biru Cerah) */
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(to right, #2563eb, #3b82f6);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        }}
        div.stButton > button[kind="primary"]:hover {{
            background: linear-gradient(to right, #1d4ed8, #2563eb);
            box-shadow: 0 6px 10px rgba(37, 99, 235, 0.3);
        }}
        
        /* 7. Utility Classes */
        .product-title {{
            font-size: 0.95rem; font-weight: 700; color: {text_color};
            line-height: 1.4; height: 2.8em; overflow: hidden;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            margin-bottom: 0.5rem;
        }}
        .metric-badge {{
            background-color: #dbeafe; color: #1e40af; /* Biru Background, Text Navy */
            padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
            border: 1px solid #bfdbfe;
        }}
        .category-card-img {{
            border-radius: 12px; overflow: hidden; 
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); 
            margin-bottom: 10px; position: relative;
        }}
        /* Warna Label Kategori diganti Biru Utama */
        .category-label {{ 
            background: #2563eb; 
            color: white; padding: 10px; text-align: center; font-weight: 600; font-size: 0.9rem; 
        }}
        </style>
    """, unsafe_allow_html=True)

def filter_by_category(df, category_name):
    """Filter dataframe menggunakan regex boundary untuk akurasi lebih tinggi."""
    df_filtered = pd.DataFrame()
    cat_lower = category_name.lower()
    
    keywords = {
        "skincare": r'\b(skin|facial|cleanser|moisturizer|serum|acne|eczema|face|lip care|vaseline|cetaphil)\b',
        "haircare": r'\b(hair|shampoo|conditioner|dandruff|styling|mousse|pantene|head & shoulders)\b',
        "make up": r'\b(makeup|lipstick|lip balm|foundation|blush|primer|mascara|eyeshadow|concealer|powder)\b',
        "bodycare": r'\b(body|bath|shower|lotion|cream|scrub|soap|deodorant|shaving|razor|body wash)\b'
    }

    if cat_lower in keywords:
        mask = df['Category'].str.contains(keywords[cat_lower], case=False, regex=True, na=False) | \
            df['Name'].str.contains(keywords[cat_lower], case=False, regex=True, na=False)
        df_filtered = df[mask]
    elif cat_lower == "others":
        all_keywords = "|".join(keywords.values())
        mask = ~df['Category'].str.contains(all_keywords, case=False, regex=True, na=False)
        df_filtered = df[mask]
    else:
        df_filtered = df[df['Category'].astype(str).str.contains(category_name, case=False, na=False)]
    
    return df_filtered

# --- Fungsi Bantu Cart ---
def add_to_cart(pid):
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if pid not in st.session_state.cart:
        st.session_state.cart.append(pid)
        st.toast(f"Produk berhasil ditambahkan ke keranjang! 🛒", icon="✅")
    else:
        st.toast(f"Produk sudah ada di keranjang!", icon="⚠️")

# ==========================================
# 2. KOMPONEN UI (Diperbarui dengan Style Code 2)
# ==========================================

def display_evaluation_ui(evaluation: HybridEvaluation):
    """Menampilkan hasil evaluasi LLM dengan gaya modern (Code 2)."""
    score = evaluation.score
    
    # Warna dinamis Code 2
    if score >= 8: color, bg_color, icon = "#22c55e", "#dcfce7", "🌟 Excellent"
    elif score >= 5: color, bg_color, icon = "#f97316", "#ffedd5", "⚖️ Moderate"
    else: color, bg_color, icon = "#ef4444", "#fee2e2", "⚠️ Low Relevance"

    st.markdown("")
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

@st.dialog("Detail Produk Lengkap", width="large")
def show_product_popup(product_data, score=None):
    """Popup modern dengan Gambar Fixed Size."""
    
    c_img, c_info = st.columns([1, 1.2], gap="medium")
    
    with c_img:
        img_url = str(product_data.get('ImageURL', '')).split('|')[0]
        
        # --- BAGIAN INI YANG DIUBAH AGAR FIXED SIZE ---
        if img_url and img_url != 'nan' and pd.notna(img_url):
            st.markdown(f"""
                <div style="
                    height: 400px;           /* TINGGI FIXED (Bisa diganti misal 300px) */
                    width: 100%;
                    background-color: #ffffff; 
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                    display: flex;           /* Flexbox untuk menengahkan gambar */
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                ">
                    <img src="{img_url}" style="
                        max-height: 100%;    /* Agar tidak melebihi kotak */
                        max-width: 100%;
                        object-fit: contain; /* KUNCI: Agar gambar pas & tidak gepeng */
                    ">
                </div>
            """, unsafe_allow_html=True)
        else:
            # Placeholder jika tidak ada gambar
            st.markdown('<div style="height:400px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:12px; color:#94a3b8; font-weight:bold;">No Image Available</div>', unsafe_allow_html=True)
        # ---------------------------------------------

    with c_info:
        st.caption(f"{product_data.get('Category', '-')} • {product_data.get('Brand', '-')}")
        st.markdown(f"## {product_data.get('Name', 'No Name')}")
        
        rating_val = int(product_data.get('Rating', product_data.get('average_rating', 0)))
        stars = "★" * rating_val + "☆" * (5 - rating_val)
        st.markdown(f"<span style='color:#f59e0b; font-size:1.2rem;'>{stars}</span> <span style='color:#64748b; font-size:0.9rem;'>({product_data.get('ReviewCount', 0)} reviews)</span>", unsafe_allow_html=True)
        
        if score:
            st.markdown(f"<span class='metric-badge'>Relevance Score: {score:.4f}</span>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Menggunakan container dengan scroll untuk deskripsi jika terlalu panjang
        with st.container(height=150, border=False):
            st.write(product_data.get('Description', 'Tidak ada deskripsi.'))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
                st.success("Pembayaran Berhasil!")

    st.markdown("---")
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
    """Merender kartu produk dengan desain 'Card' Modern (Code 2)."""
    with st.container(border=True): # Menggunakan styling CSS yang sudah diinject
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

        full_brand = row.get('Brand', '-')
        # Jika panjang lebih dari 20 karakter, potong dan tambah '...'
        if len(full_brand) > 20:
            display_brand = full_brand[:20] + "..."
        else:
            display_brand = full_brand
        
        st.markdown(f"<div class='product-title' title='{row.get('Name', 'No Name')}'>{row.get('Name', 'No Name')}</div>", unsafe_allow_html=True)
        
        c_brand, c_rate = st.columns([2, 1])
        with c_brand:
            st.caption(display_brand)
        with c_rate:
            rating_int = int(row.get('Rating', row.get('average_rating', 0)))
            st.markdown(f"⭐ **{rating_int}**")

        if 'final_score' in row:
            st.markdown(f"<div style='margin-bottom:8px;'><span class='metric-badge'>Score: {row['final_score']:.2f}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        unique_key = f"{prefix}_btn_{row.get('ProdID', row.name)}" if prefix else f"btn_{row.get('ProdID', row.name)}"
        if st.button("Lihat Detail", key=unique_key, use_container_width=True, type="primary"):
            if full_df is not None and row.name in full_df.index:
                full_data = full_df.loc[row.name]
            else:
                full_data = row
            score_val = row.get('final_score', None)
            show_product_popup(full_data, score=score_val)

def display_grid(products, title, full_df=None, prefix=""):
    if title:
        st.subheader(title)
    cols = st.columns(5)
    for idx, (_, product) in enumerate(products.iterrows()):
        with cols[idx % 5]:
            render_product_card(product, full_df=full_df, prefix=prefix)

# --- FUNGSI HEADER & FOOTER ---

def render_header(show_search_controls=False, custom_title=None):
    """
    Header global untuk halaman selain Home.
    LOGIC: Menggunakan kolom dan state dari Code 1.
    STYLE: Menggunakan ID 'header-marker' agar kena CSS gradient Code 2.
    """
    with st.container(border=True):
        st.markdown('<span id="header-marker"></span>', unsafe_allow_html=True) 
        
        # Tambahkan kolom ekstra untuk Toggle Dark Mode di ujung kanan
        if show_search_controls:
            c_back, c_logo, c_mid, c_num, c_sbtn, c_ebtn, c_mode = st.columns([0.5, 0.8, 3.2, 0.8, 0.5, 1.2, 0.5], gap="small")
        else:
            c_back, c_logo, c_mid, c_sbtn, c_mode = st.columns([0.6, 1, 5.5, 0.6, 0.5], gap="small")

        # 1. Back Button
        with c_back:
            if st.button("⬅️", help="Kembali ke Home", use_container_width=True, key=f"hdr_back_{st.session_state.get('current_page', 'unk')}"):
                st.session_state["current_page"] = "home"
                if "cat_page_number" in st.session_state:
                    st.session_state["cat_page_number"] = 0
                st.rerun()

        # 2. Logo (Ganti Text dengan Image)
        with c_logo:
            # Cek apakah file gambar ada, jika tidak pakai text fallback
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=100) # Sesuaikan width
            else:
                st.markdown("<h3 style='margin:0; padding-top:5px; color:white;'>clickmart</h3>", unsafe_allow_html=True)

        # 3. Middle (Search/Title)
        product_query = ""
        with c_mid:
            if custom_title:
                st.markdown(f"<h4 style='margin:0; padding-top:5px; color:white !important;'>{custom_title}</h4>", unsafe_allow_html=True)
            else:
                default_query = st.session_state.get("global_search_query", "")
                # AUTO SEARCH: on_change akan mentrigger rerun
                product_query = st.text_input("Cari Produk", value=default_query, placeholder="Cari...", label_visibility="collapsed", key=f"hdr_search_{st.session_state.get('current_page')}")

        # 4. Controls
        top_n = 10
        run_search = False
        run_eval = False

        if show_search_controls:
            with c_num:
                # AUTO REFRESH: Saat angka diganti, streamlit otomatis rerun dan hasil update
                top_n = st.number_input("Jml", min_value=5, max_value=50, value=10, step=5, label_visibility="collapsed", key="hdr_num")
            
            with c_sbtn:
                run_search = st.button("🔍", type="primary", use_container_width=True, key="hdr_sbtn_main")
                
            with c_ebtn:
                has_recs = 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None
                run_eval = st.button("Evaluate AI", disabled=not has_recs, use_container_width=True, key="hdr_eval")
        else:
            with c_sbtn:
                if st.button("🔍", use_container_width=True, key="hdr_sbtn_redirect"):
                    st.session_state["global_search_query"] = ""
                    st.session_state["current_page"] = "recommender"
                    st.rerun()
        
        # TOGGLE DARK MODE
        with c_mode:
            dm_on = st.toggle("🌙", value=st.session_state.dark_mode, key="dm_toggle")
            if dm_on != st.session_state.dark_mode:
                st.session_state.dark_mode = dm_on
                st.rerun()

    return product_query, top_n, run_search, run_eval

def render_footer():
    """Footer Global (Logic Code 1)."""
    st.markdown("---")
    # Styling sedikit diperbaiki tapi konten sama persis Code 1
    st.markdown("""
        <div style='background-color: #2563eb; color: #FFFFFF; padding: 20px; text-align: center; border-radius: 10px; margin-top: 20px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);'>
            <p style='margin:0; font-weight:bold;'>clickmart AI Recommender</p>
            <p style='font-size: 0.8rem; margin:0;'>Ditenagai oleh Streamlit & Google Gemini LLM</p>
            <p style='font-size: 0.8rem; margin:0;'>Developed by Kelompok 5 DSAI CAMP3</p>
        </div>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
@st.cache_resource
def initialize_system():
    try:
        df = load_local_data(DATA_FILE_PATH)
        if df.empty:
            return None, None, None, None, None

        df = clean_and_handle_missing_values(df)
        df, tfidf_matrix = create_features(df)
        
        hybrid_sim = build_hybrid_model(df, tfidf_matrix)
        metrics = calculate_evaluation_metrics(df, hybrid_sim)
        
        llm_tools = LLMTools()
        recommender = IntegratedRecommender(df, hybrid_sim)
        
        cf_recommender = CollaborativeFilteringRecommender(data_path=DATA_FILE_PATH, num_users=500, random_seed=42)
        
        return df, recommender, llm_tools, metrics, cf_recommender
        
    except Exception as e:
        logger.error(f"Error initalization: {e}")
        return None, None, None, None, None

# ==========================================
# 3. HALAMAN (PAGES)
# ==========================================

# --- Halaman: Category View (Updated with Function) ---
def page_category_view(df):
    category_name = st.session_state.get("selected_category", "Others")
    
    # [1] PANGGIL HEADER (Custom Title)
    render_header(show_search_controls=False, custom_title=
    f"""
        <div style="
            border: 1px solid #e2e8f0; 
            background-color: #f1f5f9; 
            border-radius: 8px; 
            padding: 8px 12px; 
            color: #334155; 
            font-size: 1rem; 
            display: flex; 
            align-items: center; 
            height: 42px; /* Tinggi standar tombol Streamlit */
            margin-top: 0px;
        ">
            <span style="color: #64748b; margin-right: 5px;">Kategori:</span> 
            <span style="font-weight: 600; color: #1e293b;">{category_name}</span>
        </div>
    """)

    # --- FILTERING ---
    filtered_df = filter_by_category(df, category_name)

    st.markdown(f"Found **{len(filtered_df)}** products in {category_name}")
    st.markdown("---")

    if filtered_df.empty:
        st.info(f"😔 Maaf, produk untuk kategori '{category_name}' belum tersedia.")
        render_footer() # Tetap tampilkan footer
        return

    # --- PAGINASI ---
    ITEMS_PER_PAGE = 10
    if "cat_page_number" not in st.session_state:
        st.session_state.cat_page_number = 0

    total_pages = (len(filtered_df) - 1) // ITEMS_PER_PAGE + 1
    
    if st.session_state.cat_page_number >= total_pages:
        st.session_state.cat_page_number = 0

    start_idx = st.session_state.cat_page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    batch_df = filtered_df.iloc[start_idx:end_idx]

    # --- RENDER GRID ---
    display_grid(batch_df, "", full_df=df, prefix=f"cat_{category_name}")

    # --- NAVIGASI HALAMAN ---
    st.markdown("<br>", unsafe_allow_html=True)
    c_prev, c_info, c_next = st.columns([1, 2, 1])
    
    with c_prev:
        if st.button("Previous Page", disabled=(st.session_state.cat_page_number == 0), use_container_width=True):
            st.session_state.cat_page_number -= 1
            st.rerun()
            
    with c_info:
        st.markdown(f"<div style='text-align: center; padding-top: 10px;'>Page {st.session_state.cat_page_number + 1} of {total_pages}</div>", unsafe_allow_html=True)
        
    with c_next:
        if st.button("Next Page", disabled=(st.session_state.cat_page_number >= total_pages - 1), use_container_width=True):
            st.session_state.cat_page_number += 1
            st.rerun()

    # [2] PANGGIL FOOTER
    render_footer()

# --- Halaman: Product Recommender (Logic Code 1) ---
def page_recommender(df, recommender, llm_tools, metrics, cf_recommender):
    
    # Header Code 1 (updated style)
    product_query, top_n, run_search, run_eval = render_header(show_search_controls=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Info")
        st.metric("Total SKU", len(df))
        if st.button("🔄 Reset Cache / Refresh"):
            st.cache_resource.clear()
            st.rerun()
            
        st.header("🛒 Keranjang Belanja")
        if 'cart' in st.session_state and st.session_state.cart:
            st.write(f"Items: {len(st.session_state.cart)}")
        else:
            st.write("Keranjang kosong.")
        if st.button("Kosongkan Keranjang"):
            st.session_state.cart = []
            st.success("Keranjang dikosongkan!")

    trigger_home = st.session_state.get("trigger_search", False)
    # Update global query jika user mengetik di search bar atas
    if product_query:
        st.session_state["global_search_query"] = product_query

    # Jalankan pencarian jika: Ada query DAN (Tombol ditekan ATAU trigger home aktif ATAU query berubah/visual berubah)
    # Streamlit sifatnya reaktif, jadi jika product_query ada isinya, kita jalankan saja.
    # Untuk efisiensi, kita bisa cek apakah hasil yang ada sekarang sudah sesuai query.
    
    should_run = False
    if trigger_home: 
        should_run = True
        st.session_state["trigger_search"] = False
    elif run_search:
        should_run = True
    elif product_query and product_query != st.session_state.get("last_run_query", ""):
        should_run = True # Auto search saat ngetik/enter
    elif product_query and top_n != st.session_state.get("last_run_top_n", 0):
        should_run = True # Auto refresh saat ganti jumlah visual

    if should_run or (product_query and 'current_rekom' not in st.session_state):
        
        st.session_state["last_run_query"] = product_query
        st.session_state["last_run_top_n"] = top_n

        with st.spinner(f"Mencari produk terbaik untuk '{product_query}'..."):
            # Interpretasi LLM (Opsional, bisa di-skip kalau mau cepat)
            interpreted = product_query
            if llm_tools:
                interpreted = llm_tools.interpret_query_with_llm(product_query)
            
            recs = recommender.get_recommendations(interpreted, int(top_n))

            if isinstance(recs, str) or recs.empty:
                st.session_state['current_rekom'] = None
                # === GANTI TAMPILAN TIDAK DITEMUKAN ===
                st.markdown(f"""
                <div style="text-align:center; padding: 40px; background-color: #fee2e2; border-radius: 10px; margin-top: 20px;">
                    <h3 style="color: #ef4444;">😔 Oops, Produk Tidak Ditemukan</h3>
                    <p style="color: #7f1d1d;">Kami tidak dapat menemukan produk yang cocok dengan kata kunci <strong>"{product_query}"</strong>.</p>
                    <p>Coba gunakan kata kunci yang lebih umum seperti <em>"Serum", "Lipstick", "Sabun"</em>.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state['current_rekom'] = recs
                if 'last_eval_result' in st.session_state:
                    del st.session_state['last_eval_result']
    
    # Jika tidak run search, tapi hasil kosong (User hapus search bar)
    elif not product_query:
        st.info("Silakan masukkan kata kunci produk di kolom pencarian atas ☝️")
        st.session_state['current_rekom'] = None

    if (run_search or trigger_home) and product_query:
        st.session_state.trigger_search = False 
        st.session_state["global_search_query"] = product_query
        
        with st.spinner(f"Mencari produk terbaik untuk '{product_query}'..."):
            interpreted = product_query
            if llm_tools:
                interpreted = llm_tools.interpret_query_with_llm(product_query)
            
            if interpreted != product_query:
                st.info(f"💡 Query diperjelas AI: **{interpreted}**")

            recs = recommender.get_recommendations(interpreted, int(top_n))

            if isinstance(recs, str) or recs.empty:
                st.error("Tidak ada produk ditemukan.")
                st.session_state['current_rekom'] = None
            else:
                st.session_state['current_rekom'] = recs
                if 'last_eval_result' in st.session_state:
                    del st.session_state['last_eval_result']
        
        st.rerun()

    # Logic Eval Code 1
    if run_eval and 'current_rekom' in st.session_state:
        if not llm_tools:
            st.error("LLM Tools error.")
        else:
            with st.spinner("Gemini sedang menganalisis hasil..."):
                eval_res = llm_tools.evaluate_recommendation_with_llm(st.session_state['current_rekom'])
                if eval_res:
                    st.session_state['last_eval_result'] = eval_res

    # Main Display
    if 'last_eval_result' in st.session_state:
        with st.expander("📝 Lihat Hasil Analisis & Evaluasi AI", expanded=True):
            display_evaluation_ui(st.session_state['last_eval_result'])

    if 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None:
        recs = st.session_state['current_rekom']
        # Gunakan Grid baru
        display_grid(recs, f"Hasil Pencarian ({len(recs)} Produk)", full_df=df, prefix="search")

    # EDA Footer Code 1
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.expander("📊 Klik untuk membuka Analisis Data (EDA) & Statistik Dataset"):
        st.subheader("Exploratory Data Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='text-align: center; font-weight: bold;'>Distribusi Rating Produk</div>", unsafe_allow_html=True)
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.histplot(df['Rating'], bins=10, kde=True, ax=ax1, color='teal')
            st.pyplot(fig1)

        with c2:
            st.markdown("Kategori Terpopuler")
            st.bar_chart(df['Category'].value_counts().head(10), color='#3b82f6')

        col_kiri, col_tengah, col_kanan = st.columns([1, 2, 1]) # Atur rasio agar tengah pas
        with col_tengah:
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 10px;'>Sample Heatmap Kemiripan</div>", unsafe_allow_html=True)
            n_viz = min(10, len(df))
            sample_indices = range(n_viz)
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            sns.heatmap(recommender.hybrid_sim[np.ix_(sample_indices, sample_indices)], cmap='YlGnBu', ax=ax3, cbar_kws={"shrink": .7})
            st.pyplot(fig3, use_container_width=False)
            
    render_footer()

# --- Halaman: Home Page (STRUKTUR HEADER & FOOTER DARI CODE 1) ---

def page_home(df, cf_recommender):
    # 1. Header Home
    with st.container(border=True):
        c_logo, c_search, c_btn = st.columns([1.2, 4.3, 0.5], gap="small")

        with c_logo:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=150)
            else:
                st.markdown("""
                    <div style='font-size: 30px; font-weight: 900; color: #2563eb; margin-top: -5px;'>
                        clickmart
                    </div>
                """, unsafe_allow_html=True)

        with c_search:
            search_input = st.text_input("Search", placeholder="Cari produk di clickmart...", label_visibility="collapsed")

        with c_btn:
            if st.button("🔍", key="search_home", use_container_width=True):
                if search_input:
                    st.session_state["global_search_query"] = search_input
                    st.session_state["trigger_search"] = True
                    st.session_state["current_page"] = "recommender"
                    st.rerun()

    if search_input:
        st.session_state["global_search_query"] = search_input
        st.session_state["trigger_search"] = True
        st.session_state["current_page"] = "recommender"
        st.rerun()

    # ==========================================
    # [BARU] CSS CAROUSEL (SLIDESHOW) SECTION
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True) 

    # Link Gambar Banner
    img1 = "https://i.pinimg.com/1200x/94/76/7e/94767ef965cba55540a8ebc875aae1cc.jpg"
    img2 = "https://i.pinimg.com/1200x/e8/c1/b6/e8c1b61a863d1be4a2a1b03bcbd2aee3.jpg"
    img3 = "https://i.pinimg.com/736x/dc/a6/36/dca6368b8a4563b0d1de85ec1efc677d.jpg"

    # HTML & CSS untuk Carousel Otomatis
    carousel_html = f"""
    <style>
        /* Container Utama Slider */
        .slider-frame {{ 
            overflow: hidden; 
            width: 100%; 
            height: 300px;  /* <--- TINGGI FIX (Sesuaikan jika ingin lebih pendek/tinggi) */
            border-radius: 12px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
            margin-bottom: 20px; 
        }}

        /* Container Geser (Width 300% untuk 3 gambar) */
        .slide-images {{
            width: 300%;
            display: flex;
            animation: slide_animation 12s infinite; /* Durasi total animasi */
        }}

        /* Setiap Gambar (Width 1/3 dari container geser) */
        .img-container {{
            width: 33.333%;
            position: relative;
        }}

        .img-container img {{
            width: 100%;
            height: auto;
            display: block;
            object-fit: cover;
            /* Opsional: Membatasi tinggi maksimum agar tidak terlalu panjang */
            max-height: 400px; 
            min-height: 200px;
        }}

        /* Keyframes untuk Animasi Geser */
        @keyframes slide_animation {{
            0% {{ margin-left: 0; }}
            30% {{ margin-left: 0; }}       /* Tahan gambar 1 */
            
            33% {{ margin-left: -100%; }}   /* Geser ke gambar 2 */
            63% {{ margin-left: -100%; }}   /* Tahan gambar 2 */
            
            66% {{ margin-left: -200%; }}   /* Geser ke gambar 3 */
            96% {{ margin-left: -200%; }}   /* Tahan gambar 3 */
            
            100% {{ margin-left: 0; }}      /* Kembali ke awal */
        }}
    </style>

    <div class="slider-frame">
        <div class="slide-images">
            <div class="img-container">
                <img src="{img1}" alt="Banner 1">
            </div>
            <div class="img-container">
                <img src="{img2}" alt="Banner 2">
            </div>
            <div class="img-container">
                <img src="{img3}" alt="Banner 3">
            </div>
        </div>
    </div>
    """
    
    # Render Carousel
    st.markdown(carousel_html, unsafe_allow_html=True)
    # ==========================================

    # 2. Categories (Code 1 Layout + Code 2 Styling via CSS)
    st.markdown("### 🛍️ Kategori Pilihan")
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
            with st.container():
                # 1. RENDER GAMBAR (VISUAL) DULUAN
                st.markdown(f"""
                <div class="category-card-img">
                    <img src="{category['image']}" alt="{category['name']}" style="width: 100%; height: 100px; object-fit: cover;">
                    <div class="category-label">{category['name']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. RENDER TOMBOL (KLIK) BELAKANGAN
                # Tombol ini akan ditarik ke atas oleh CSS
                if st.button(" ", key=f"cat_btn_{i}", use_container_width=True):
                    st.session_state["selected_category"] = category["name"]
                    st.session_state["current_page"] = "category_view"
                    st.session_state["cat_page_number"] = 0 
                    st.rerun()

    # --- GANTI BAGIAN CSS DI page_home (BAWAH LOOP KATEGORI) DENGAN INI ---
    st.markdown("""
    <style>
    /* Styling Visual Kartu */
    .category-card-img {
        border-radius: 12px; 
        overflow: hidden; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); /* Shadow Biru */
        margin-bottom: 0px; 
        transition: all 0.3s ease; 
    }
    .category-card-img:hover { 
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3); /* Hover effect biru */
        transform: translateY(-3px); 
    }
    .category-label { 
        background: #2563eb; /* GANTI WARNA INI JADI BIRU UTAMA */
        color: white; 
        padding: 10px; 
        text-align: center; 
        font-weight: 600; 
        font-size: 0.9rem; 
    }

    /* TEKNIK NEGATIVE MARGIN (Tetap sama) */
    div[class*="st-key-cat_btn"] {
        margin-top: -145px !important; 
        position: relative !important; 
        z-index: 10 !important;
        opacity: 0 !important; 
        height: 145px !important; 
        overflow: hidden;
    }

    div[class*="st-key-cat_btn"] > button {
        height: 100% !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Best Sellers & Featured
    if cf_recommender:
        most_liked = cf_recommender.get_most_liked_products(top_n=5)
        if not most_liked.empty:
            display_grid(most_liked, "🔥 Produk Terlaris", full_df=df, prefix="best")

    st.subheader("✨ Produk Unggulan Kami")
    display_df = df[df['ImageURL'].notna() & (df['ImageURL'] != '')].head(15)
    
    cols = st.columns(5)
    for idx, (index, row) in enumerate(display_df.iterrows()):
        with cols[idx % 5]:
            render_product_card(row, full_df=df, prefix="feat")

    if cf_recommender:
        recom_prods = cf_recommender.get_most_liked_products(top_n=15)
        if not recom_prods.empty:
            display_grid(recom_prods, "❤️ Rekomendasi Untuk Anda", full_df=df, prefix="recom")

    # Footer
    render_footer()

# --- Main Controller ---

def main():
    st.set_page_config(page_title="clickmart", page_icon=ICON_PATH, layout="wide")

    # Inject CSS Code 2
    inject_custom_css()

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    df, recommender, llm_tools, metrics, cf_recommender = initialize_system()

    if df is None:
        st.error("Data tidak ditemukan. Pastikan file CSV tersedia.")
        return

    # Routing
    if st.session_state["current_page"] == "home":
        page_home(df, cf_recommender)
    elif st.session_state["current_page"] == "recommender":
        page_recommender(df, recommender, llm_tools, metrics, cf_recommender)
    elif st.session_state["current_page"] == "category_view":
        page_category_view(df)

if __name__ == "__main__":
    main()