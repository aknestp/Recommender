import streamlit as st
import pandas as pd
import time
from components.logic import add_to_cart

def display_evaluation_ui(evaluation):
    score = evaluation.score
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
    c_img, c_info = st.columns([1, 1.2], gap="medium")
    
    with c_img:
        img_url = str(product_data.get('ImageURL', '')).split('|')[0]
        if img_url and img_url != 'nan' and pd.notna(img_url):
            st.markdown(f"""
                <div style="height: 400px; width: 100%; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; justify-content: center; align-items: center; overflow: hidden;">
                    <img src="{img_url}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="height:400px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:12px; color:#94a3b8; font-weight:bold;">No Image Available</div>', unsafe_allow_html=True)

    with c_info:
        st.caption(f"{product_data.get('Category', '-')} • {product_data.get('Brand', '-')}")
        st.markdown(f"## {product_data.get('Name', 'No Name')}")
        
        rating_val = int(product_data.get('Rating', product_data.get('average_rating', 0)))
        stars = "★" * rating_val + "☆" * (5 - rating_val)
        st.markdown(f"<span style='color:#f59e0b; font-size:1.2rem;'>{stars}</span> <span style='color:#64748b; font-size:0.9rem;'>({product_data.get('ReviewCount', 0)} reviews)</span>", unsafe_allow_html=True)
        
        if score:
            st.markdown(f"<span class='metric-badge'>Relevance Score: {score:.4f}</span>", unsafe_allow_html=True)

        st.markdown("---")
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
    with st.container(border=True): 
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
        display_brand = full_brand[:20] + "..." if len(full_brand) > 20 else full_brand
        
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
            full_data = full_df.loc[row.name] if full_df is not None and row.name in full_df.index else row
            show_product_popup(full_data, score=row.get('final_score', None))

def display_grid(products, title, full_df=None, prefix=""):
    if title:
        st.subheader(title)
    cols = st.columns(5)
    for idx, (_, product) in enumerate(products.iterrows()):
        with cols[idx % 5]:
            render_product_card(product, full_df=full_df, prefix=prefix)