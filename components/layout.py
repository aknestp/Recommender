import streamlit as st
import os

# --- Konfigurasi Global ---
DATA_FILE_PATH = 'data/product_data.csv'
LOGO_PATH = 'assets/logo.png' 
ICON_PATH = 'assets/icon.png'

def inject_custom_css(dark_mode):
    # --- PALET WARNA BARU ---
    primary_color = "#385F8C" # Biru Utama
    secondary_bg = "#E9E9E9"  # Abu Terang (untuk tombol detail)
    card_bg = "#FFFFFF"       # Background Card Putih
    header_bg = "#FFFFFF"     # Background Header PUTIH
    text_color = "#385F8C"    # Teks Utama Biru
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        /* 1. Global Typography */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {text_color};
        }}
        
        /* Judul Section */
        h1, h2, h3, h4, h5, h6 {{
            color: {primary_color} !important;
        }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: {primary_color} !important;
        }}

        /* 2. Card Container Style */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg};
            border: 1px solid #d1d5db;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 1rem;
        }}
        
        /* Teks di dalam Card */
        [data-testid="stVerticalBlockBorderWrapper"] p,
        [data-testid="stVerticalBlockBorderWrapper"] span,
        [data-testid="stVerticalBlockBorderWrapper"] div {{
            color: {text_color} !important;
        }}
        
        /* 3. HEADER STYLE (Background Putih) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) {{
            background: {header_bg}; /* Putih */
            border: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-bottom: 1px solid #f1f5f9;
        }}
        
        /* FIX: Teks di Header jadi BIRU (karena background putih) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) * {{
            color: {primary_color} !important;
        }}
        
        /* 4. BUTTON STYLING */
        /* A. Tombol Primary (Search, Buy Now) - Biru */
        div.stButton > button[kind="primary"] {{
            background: {primary_color};
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        
        /* B. Tombol Secondary (Lihat Detail) - Abu E9E9E9 */
        div.stButton > button[kind="secondary"] {{
            background-color: {secondary_bg} !important;
            color: {primary_color} !important; 
            border: none !important;
            border-radius: 8px;
            font-weight: 600;
        }}
        div.stButton > button[kind="secondary"]:hover {{
            background-color: #d1d5db !important;
        }}

        /* C. Tombol di Header (Back Button) - Abu Muda */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) button {{
            background-color: #f1f5f9 !important;
            color: {primary_color} !important;
            border: 1px solid #e2e8f0 !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) button:hover {{
            background-color: #e2e8f0 !important;
        }}

        /* 5. Input Field di Header (Search Bar) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) div[data-baseweb="input"] > div {{
            background-color: #f8fafc !important; 
            border: 1px solid #cbd5e1 !important;
            color: {primary_color} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) input {{
            color: {primary_color} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) input::placeholder {{
            color: #94a3b8 !important;
        }}

        /* 6. Utility Classes */
        .product-title {{
            font-size: 0.95rem; font-weight: 700;
            color: {text_color} !important;
            line-height: 1.4; height: 2.8em; overflow: hidden;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            margin-bottom: 0.5rem;
        }}
        .metric-badge {{
            background-color: #dbeafe;
            color: #1d4ed8;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        /* 7. KHUSUS FOOTER TEXT (Agar Tetap Putih) */
        .footer-text, .footer-text p, .footer-text span {{
            color: #FFFFFF !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_header(show_search_controls=False, custom_title=None):
    with st.container(border=True):
        st.markdown('<span id="header-marker"></span>', unsafe_allow_html=True) 
        
        if show_search_controls:
            c_back, c_logo, c_mid, c_num, c_sbtn, c_ebtn = st.columns([0.5, 0.8, 3.2, 0.8, 0.5, 1.2], gap="small")
        else:
            c_back, c_logo, c_mid, c_sbtn = st.columns([0.6, 1, 5.5, 0.6], gap="small")

        with c_back:
            if st.button("⬅️", help="Kembali ke Home", use_container_width=True, key=f"hdr_back_{st.session_state.get('current_page', 'unk')}"):
                st.session_state["current_page"] = "home"
                if "cat_page_number" in st.session_state:
                    st.session_state["cat_page_number"] = 0
                st.rerun()

        with c_logo:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=100)
            else:
                # Warna teks logo jadi BIRU
                st.markdown("<h3 style='margin:0; padding-top:5px; color:#385F8C;'>clickmart</h3>", unsafe_allow_html=True)

        product_query = ""
        with c_mid:
            if custom_title:
                # Warna custom title jadi BIRU
                st.markdown(f"<h4 style='margin:0; padding-top:5px; color:#385F8C !important;'>{custom_title}</h4>", unsafe_allow_html=True)
            else:
                default_query = st.session_state.get("global_search_query", "")
                product_query = st.text_input("Cari Produk", value=default_query, placeholder="Cari...", label_visibility="collapsed", key=f"hdr_search_{st.session_state.get('current_page')}")

        top_n = 10
        run_search = False
        run_eval = False

        if show_search_controls:
            with c_num:
                top_n = st.number_input("Jml", min_value=5, max_value=50, value=10, step=5, label_visibility="collapsed", key="hdr_num")
            
            with c_sbtn:
                run_search = st.button("🔍", use_container_width=True, key="hdr_sbtn_main")
                
            with c_ebtn:
                has_recs = 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None
                run_eval = st.button("Evaluate AI", disabled=not has_recs, use_container_width=True, key="hdr_eval")
        else:
            with c_sbtn:
                if st.button("🔍", use_container_width=True, key="hdr_sbtn_redirect"):
                    st.session_state["global_search_query"] = ""
                    st.session_state["current_page"] = "recommender"
                    st.rerun()
        
    return product_query, top_n, run_search, run_eval

def render_footer():
    st.markdown("---")
    # Menggunakan class 'footer-text' untuk memaksa warna putih
    st.markdown("""
        <div class="footer-text" style='background-color: #385F8C; padding: 20px; text-align: center; border-radius: 10px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0, 0.1);'>
            <p style='font-size: 1.3rem; margin:0; font-weight:bold; color: #FFFFFF !important;'>clickmart AI Recommender</p>
            <p style='font-size: 0.8rem; margin:0; color: #FFFFFF !important;'>Ditenagai oleh Streamlit & Google Gemini LLM</p>
            <p style='font-size: 0.8rem; margin:0; color: #FFFFFF !important;'>Developed by Kelompok 5 DSAI CAMP3</p>
        </div>
    """, unsafe_allow_html=True)