import streamlit as st
import pandas as pd

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

def add_to_cart(pid):
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if pid not in st.session_state.cart:
        st.session_state.cart.append(pid)
        st.toast(f"Produk berhasil ditambahkan ke keranjang! 🛒", icon="✅")
    else:
        st.toast(f"Produk sudah ada di keranjang!", icon="⚠️")