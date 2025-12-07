import streamlit as st
import os
from components.layout import render_footer, LOGO_PATH
from components.cards import display_grid, render_product_card

def show(df, cf_recommender):
    # 1. Header Khusus Home (Custom)
    with st.container(border=True):
        c_logo, c_search, c_btn = st.columns([1.2, 4.3, 0.5], gap="small")

        with c_logo:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=150)
            else:
                st.markdown("<h3 style='color: #2563eb; margin-top: -5px;'>clickmart</h3>", unsafe_allow_html=True)

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

    # 2. Carousel / Slideshow
    st.markdown("<br>", unsafe_allow_html=True) 
    img1, img2, img3 = "https://i.pinimg.com/1200x/94/76/7e/94767ef965cba55540a8ebc875aae1cc.jpg", "https://i.pinimg.com/1200x/e8/c1/b6/e8c1b61a863d1be4a2a1b03bcbd2aee3.jpg", "https://i.pinimg.com/736x/dc/a6/36/dca6368b8a4563b0d1de85ec1efc677d.jpg"
    
    st.markdown(f"""
    <style>
        .slider-frame {{ overflow: hidden; width: 100%; height: 300px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .slide-images {{ width: 300%; display: flex; animation: slide_animation 12s infinite; }}
        .img-container {{ width: 33.333%; position: relative; }}
        .img-container img {{ width: 100%; height: auto; display: block; object-fit: cover; max-height: 400px; min-height: 200px; }}
        @keyframes slide_animation {{ 0% {{ margin-left: 0; }} 30% {{ margin-left: 0; }} 33% {{ margin-left: -100%; }} 63% {{ margin-left: -100%; }} 66% {{ margin-left: -200%; }} 96% {{ margin-left: -200%; }} 100% {{ margin-left: 0; }} }}
    </style>
    <div class="slider-frame"><div class="slide-images">
        <div class="img-container"><img src="{img1}"></div>
        <div class="img-container"><img src="{img2}"></div>
        <div class="img-container"><img src="{img3}"></div>
    </div></div>
    """, unsafe_allow_html=True)

    # 3. Kategori Pilihan
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
                st.markdown(f"""
                <div class="category-card-img" style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); margin-bottom: 0px;">
                    <img src="{category['image']}" style="width: 100%; height: 100px; object-fit: cover;">
                    <div style="background: #2563eb; color: white; padding: 10px; text-align: center; font-weight: 600; font-size: 0.9rem;">{category['name']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Invisible Button Overlay
                st.markdown("""<style>div[class*="st-key-cat_btn"] { margin-top: -145px !important; position: relative !important; z-index: 10 !important; opacity: 0 !important; height: 145px !important; overflow: hidden; }</style>""", unsafe_allow_html=True)
                
                if st.button(" ", key=f"cat_btn_{i}", use_container_width=True):
                    st.session_state["selected_category"] = category["name"]
                    st.session_state["current_page"] = "category_view"
                    st.session_state["cat_page_number"] = 0 
                    st.rerun()
    st.markdown("---")

    # 4. Best Sellers
    if cf_recommender:
        most_liked = cf_recommender.get_most_liked_products(top_n=5)
        if not most_liked.empty:
            display_grid(most_liked, "🔥 Produk Terlaris", prefix="best")

    # 5. Featured
    st.subheader("✨ Produk Unggulan Kami")
    display_df = df[df['ImageURL'].notna() & (df['ImageURL'] != '')].head(15)
    cols = st.columns(5)
    for idx, (index, row) in enumerate(display_df.iterrows()):
        with cols[idx % 5]:
            render_product_card(row, full_df=df, prefix="feat")

    # 6. Recommendation
    if cf_recommender:
        recom_prods = cf_recommender.get_most_liked_products(top_n=15)
        if not recom_prods.empty:
            # HAPUS full_df=df
            display_grid(recom_prods, "❤️ Rekomendasi Untuk Anda", prefix="recom")

    render_footer()