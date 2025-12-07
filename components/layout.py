import streamlit as st
import os

# --- Konfigurasi Global ---
DATA_FILE_PATH = 'data/product_data.csv'
LOGO_PATH = 'assets/logo.png' 
ICON_PATH = 'assets/icon2.png'

def inject_custom_css(dark_mode):
    # Tentukan palet warna Biru & Putih
    if dark_mode:
        # DARK MODE
        bg_color = "#0f172a"
        text_color = "#f1f5f9"
        card_bg = "#1e293b"
        border_color = "#334155"
        input_bg = "#1e293b"
        header_grad = "linear-gradient(135deg, #020617 0%, #1e3a8a 100%)" 
    else:
        # LIGHT MODE
        bg_color = "#ffffff"        
        text_color = "#1e3a8a"
        card_bg = "#ffffff"
        border_color = "#bfdbfe"
        input_bg = "#ffffff"
        header_grad = "linear-gradient(135deg, #2563eb 0%, #60a5fa 100%)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {text_color}; }}
        .stApp {{ background-color: {bg_color}; }}
        .block-container {{ padding-top: 3rem !important; padding-bottom: 2rem !important; }}
        h1, h2, h3, h4, h5, h6, p, span, div {{ color: {text_color}; }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: {text_color} !important; }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
            padding: 1rem;
        }}
        
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) {{
            background: {header_grad};
            border: none;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(#header-marker) * {{ color: white !important; }}

        div[data-baseweb="input"] > div {{
            background-color: {input_bg} !important;
            border-color: {border_color} !important;
            color: {text_color} !important;
        }}
        input[class*="st-"] {{ color: {text_color} !important; }}
        
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(to right, #2563eb, #3b82f6);
            color: white; border: none; border-radius: 8px; font-weight: 600;
            transition: all 0.2s; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        }}
        div.stButton > button[kind="primary"]:hover {{
            background: linear-gradient(to right, #1d4ed8, #2563eb);
            box-shadow: 0 6px 10px rgba(37, 99, 235, 0.3);
        }}
        
        .product-title {{
            font-size: 0.95rem; font-weight: 700; color: {text_color};
            line-height: 1.4; height: 2.8em; overflow: hidden;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            margin-bottom: 0.5rem;
        }}
        .metric-badge {{
            background-color: #dbeafe; color: #1e40af;
            padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
            border: 1px solid #bfdbfe;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_header(show_search_controls=False, custom_title=None):
    with st.container(border=True):
        st.markdown('<span id="header-marker"></span>', unsafe_allow_html=True) 
        
        if show_search_controls:
            c_back, c_logo, c_mid, c_num, c_sbtn, c_ebtn, c_mode = st.columns([0.5, 0.8, 3.2, 0.8, 0.5, 1.2, 0.5], gap="small")
        else:
            c_back, c_logo, c_mid, c_sbtn, c_mode = st.columns([0.6, 1, 5.5, 0.6, 0.5], gap="small")

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
                st.markdown("<h3 style='margin:0; padding-top:5px; color:white;'>clickmart</h3>", unsafe_allow_html=True)

        product_query = ""
        with c_mid:
            if custom_title:
                st.markdown(f"<h4 style='margin:0; padding-top:5px; color:white !important;'>{custom_title}</h4>", unsafe_allow_html=True)
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
        
        with c_mode:
            dm_on = st.toggle("🌙", value=st.session_state.dark_mode, key="dm_toggle")
            if dm_on != st.session_state.dark_mode:
                st.session_state.dark_mode = dm_on
                st.rerun()

    return product_query, top_n, run_search, run_eval

def render_footer():
    st.markdown("---")
    st.markdown("""
        <div style='background-color: #2563eb; color: #FFFFFF; padding: 20px; text-align: center; border-radius: 10px; margin-top: 20px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);'>
            <p style='margin:0; font-weight:bold;'>clickmart AI Recommender</p>
            <p style='font-size: 0.8rem; margin:0;'>Ditenagai oleh Streamlit & Google Gemini LLM</p>
            <p style='font-size: 0.8rem; margin:0;'>Developed by Kelompok 5 DSAI CAMP3</p>
        </div>
    """, unsafe_allow_html=True)