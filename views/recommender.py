import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from components.layout import render_header, render_footer
from components.cards import display_grid, display_evaluation_ui

def show(df, recommender, llm_tools, metrics, cf_recommender):
    product_query, top_n, run_search, run_eval = render_header(show_search_controls=True)

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
    if product_query:
        st.session_state["global_search_query"] = product_query

    should_run = trigger_home or run_search
    if not should_run and product_query and product_query != st.session_state.get("last_run_query", ""):
        should_run = True

    if should_run or (product_query and 'current_rekom' not in st.session_state):
        if trigger_home: st.session_state["trigger_search"] = False
        st.session_state["last_run_query"] = product_query
        
        with st.spinner(f"Mencari produk terbaik untuk '{product_query}'..."):
            interpreted = product_query
            if llm_tools:
                interpreted = llm_tools.interpret_query_with_llm(product_query)
                if interpreted != product_query:
                    st.info(f"💡 Query diperjelas AI: **{interpreted}**")
            
            recs = recommender.get_recommendations(interpreted, int(top_n))

            if isinstance(recs, str) or recs.empty:
                st.session_state['current_rekom'] = None
                st.markdown(f"""<div style="text-align:center; padding: 40px; background-color: #fee2e2; border-radius: 10px; margin-top: 20px;">
                    <h3 style="color: #ef4444;">😔 Oops, Produk Tidak Ditemukan</h3></div>""", unsafe_allow_html=True)
            else:
                st.session_state['current_rekom'] = recs
                if 'last_eval_result' in st.session_state: del st.session_state['last_eval_result']

    elif not product_query:
        st.info("Silakan masukkan kata kunci produk di kolom pencarian atas ☝️")
        st.session_state['current_rekom'] = None

    if run_eval and 'current_rekom' in st.session_state and llm_tools:
        with st.spinner("Gemini sedang menganalisis hasil..."):
            eval_res = llm_tools.evaluate_recommendation_with_llm(st.session_state['current_rekom'])
            if eval_res: st.session_state['last_eval_result'] = eval_res

    # Main Display
    if 'last_eval_result' in st.session_state:
        with st.expander("📝 Lihat Hasil Analisis & Evaluasi AI", expanded=True):
            display_evaluation_ui(st.session_state['last_eval_result'])

    if 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None:
        recs = st.session_state['current_rekom']
        display_grid(recs, f"Hasil Pencarian ({len(recs)} Produk)", full_df=df, prefix="search")

    # EDA Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.expander("📊 Klik untuk membuka Analisis Data (EDA) & Statistik Dataset"):
        st.subheader("Exploratory Data Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("Distribusi Rating Produk")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.histplot(df['Rating'], bins=10, kde=True, ax=ax1, color='teal')
            st.pyplot(fig1)
        with c2:
            st.markdown("Kategori Terpopuler")
            st.bar_chart(df['Category'].value_counts().head(10), color='#3b82f6')
            
    render_footer()