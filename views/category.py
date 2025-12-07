import streamlit as st
from components.layout import render_header, render_footer
from components.logic import filter_by_category
from components.cards import display_grid

def show(df):
    category_name = st.session_state.get("selected_category", "Others")
    
    render_header(show_search_controls=False, custom_title=
    f"""<div style="background-color: #f1f5f9; border-radius: 8px; padding: 8px 12px; color: #334155; display: flex; align-items: center; height: 42px;">
        <span style="color: #64748b; margin-right: 5px;">Kategori:</span> 
        <span style="font-weight: 600; color: #1e293b;">{category_name}</span>
    </div>""")

    filtered_df = filter_by_category(df, category_name)
    st.markdown(f"Found **{len(filtered_df)}** products in {category_name}")
    st.markdown("---")

    if filtered_df.empty:
        st.info(f"😔 Maaf, produk untuk kategori '{category_name}' belum tersedia.")
        render_footer()
        return

    # Paginasi
    ITEMS_PER_PAGE = 10
    if "cat_page_number" not in st.session_state: st.session_state.cat_page_number = 0
    total_pages = (len(filtered_df) - 1) // ITEMS_PER_PAGE + 1
    if st.session_state.cat_page_number >= total_pages: st.session_state.cat_page_number = 0

    start_idx = st.session_state.cat_page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    batch_df = filtered_df.iloc[start_idx:end_idx]

    display_grid(batch_df, "", full_df=df, prefix=f"cat_{category_name}")

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

    render_footer()