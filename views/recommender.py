import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from components.layout import render_header, render_footer
from components.cards import display_grid, display_evaluation_ui
from src.visualisasi import (
    plot_rating_distribution, 
    plot_top_categories, 
    plot_review_count_distribution, 
    plot_correlation_heatmap
)

def show(df, recommender, llm_tools, metrics, cf_recommender):
    # 1. Render Header
    product_query, top_n, run_search, run_eval = render_header(show_search_controls=True)

    # 2. Sidebar
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

    # 3. Logic Trigger Pencarian
    trigger_home = st.session_state.get("trigger_search", False)
    
    # Update Query Global
    if product_query:
        st.session_state["global_search_query"] = product_query

    # Cek kondisi apakah harus searching
    should_run = trigger_home or run_search
    # Auto-run jika query diketik manual (Enter) dan berbeda dari sebelumnya
    if not should_run and product_query and product_query != st.session_state.get("last_run_query", ""):
        should_run = True

    # --- PROSES PENCARIAN ---
    if should_run:
        # Reset state sebelum mencari
        if trigger_home: st.session_state["trigger_search"] = False
        st.session_state["last_run_query"] = product_query
        
        # Reset error lama saat pencarian baru dimulai
        if 'search_error' in st.session_state:
            del st.session_state['search_error']
        
        with st.spinner(f"Mencari produk terbaik untuk '{product_query}'..."):
            interpreted = product_query
            if llm_tools:
                interpreted = llm_tools.interpret_query_with_llm(product_query)
                if interpreted != product_query:
                    st.info(f"💡 Query diperjelas AI: **{interpreted}**")
            
            recs = recommender.get_recommendations(interpreted, int(top_n))

            if isinstance(recs, str) or recs.empty:
                # KASUS TIDAK DITEMUKAN
                st.session_state['current_rekom'] = None
                
                # Hapus hasil evaluasi lama
                if 'last_eval_result' in st.session_state: 
                    del st.session_state['last_eval_result']
                
                # Simpan Error ke State agar bertahan setelah rerun
                st.session_state['search_error'] = True
                
                # Rerun untuk update Header (Disable tombol Evaluate)
                st.rerun()

            else:
                # KASUS DITEMUKAN
                st.session_state['current_rekom'] = recs
                # Hapus error jika ada
                if 'search_error' in st.session_state:
                    del st.session_state['search_error']
                # Hapus evaluasi lama
                if 'last_eval_result' in st.session_state: 
                    del st.session_state['last_eval_result']
                
                # Rerun untuk update Header (Enable tombol Evaluate)
                st.rerun()

    # --- TAMPILAN ERROR (Di luar blok search agar muncul setelah rerun) ---
    if st.session_state.get('search_error'):
        st.markdown(f"""<div style="text-align:center; padding: 40px; background-color: #fee2e2; border-radius: 10px; margin-top: 20px;">
            <h3 style="color: #ef4444;">😔 Oops, Produk Tidak Ditemukan</h3>
            <p style="color: #7f1d1d;">Kami tidak dapat menemukan produk yang cocok dengan kata kunci tersebut.</p>
            </div>""", unsafe_allow_html=True)
        
    elif not product_query:
        st.info("Silakan masukkan kata kunci produk di kolom pencarian atas ☝️")
        st.session_state['current_rekom'] = None

    # --- LOGIC EVALUATE AI ---
    if run_eval and 'current_rekom' in st.session_state and llm_tools:
        with st.spinner("Gemini sedang menganalisis hasil..."):
            eval_res = llm_tools.evaluate_recommendation_with_llm(st.session_state['current_rekom'])
            if eval_res: st.session_state['last_eval_result'] = eval_res

    # --- TAMPILAN HASIL (Main Display) ---
    
    # 1. Tampilkan Hasil Evaluasi AI
    if 'last_eval_result' in st.session_state:
        with st.expander("📝 Lihat Hasil Analisis & Evaluasi AI", expanded=True):
            display_evaluation_ui(st.session_state['last_eval_result'])

    # 2. Tampilkan Grid Produk
    if 'current_rekom' in st.session_state and st.session_state['current_rekom'] is not None:
        recs = st.session_state['current_rekom']
        display_grid(recs, f"Hasil Pencarian ({len(recs)} Produk)", full_df=df, prefix="search")

    # --- EDA Footer (GLOBAL SWITCH VERSION) ---
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.expander("📊 Klik untuk membuka Analisis Data (EDA) & Statistik Dataset"):
        st.subheader("Exploratory Data Analysis")
        
        # === GLOBAL SWITCH ===
        # Satu tombol untuk mengatur semua grafik
        c1, c2 = st.columns(2)
        with c1:
            use_interactive = st.toggle("🔄 Aktifkan Mode Interaktif untuk Semua Grafik", value=False)
        
        with c2:
            if use_interactive:
                st.markdown("ℹ️ *Mode Interaktif: Grafik bisa di-zoom, hover, dan tabel bisa di-sort.*")
            else:
                st.markdown("ℹ️ *Mode Statis: Tampilan standar laporan menggunakan Matplotlib.*")
        
        st.markdown("---")

        # --- BARIS 1 ---
        c1, c2 = st.columns(2)
        
        # FIG 1: Distribusi Rating
        with c1:
            st.markdown("**1. Distribusi Rating Produk**")
            if use_interactive:
                rating_counts = df['Rating'].round(1).value_counts().sort_index()
                st.bar_chart(rating_counts, color='#385F8C')
            else:
                st.pyplot(plot_rating_distribution(df))

        # FIG 2: Top Kategori
        with c2:
            st.markdown("**2. Kategori Terpopuler**")
            if use_interactive:
                top_cats = df['Category'].value_counts().head(10)
                st.bar_chart(top_cats, color='#385F8C')
            else:
                st.pyplot(plot_top_categories(df))

        st.markdown("<br>", unsafe_allow_html=True) # Spasi antar baris

        # --- BARIS 2 ---
        c3, c4 = st.columns(2)
        
        # FIG 3: Distribusi Review Count
        with c3:
            st.markdown("**3. Distribusi Jumlah Review**")
            if use_interactive:
                review_bins = pd.cut(df['ReviewCount'], bins=15).value_counts().sort_index()
                review_bins.index = review_bins.index.astype(str)
                st.bar_chart(review_bins, color='#385F8C')
            else:
                st.pyplot(plot_review_count_distribution(df))
            
        # FIG 4: Korelasi Heatmap
        with c4:
            st.markdown("**4. Korelasi Rating vs Review**")
            if use_interactive:
                numeric_df = df.select_dtypes(include=[np.number])
                corr_matrix = numeric_df[['Rating', 'ReviewCount']].corr()
                st.dataframe(
                    corr_matrix.style.background_gradient(cmap='Blues'),
                    use_container_width=True
                )
            else:
                st.pyplot(plot_correlation_heatmap(df))
            
    render_footer()