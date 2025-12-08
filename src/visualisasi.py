# src/visualisasi.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

# Set Style Global (Opsional)
sns.set_style("whitegrid")
COLOR_PALETTE = '#385F8C'

def plot_rating_distribution(df: pd.DataFrame):
    """Plot 1: Distribusi Rating"""
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(df['Rating'], bins=20, kde=True, ax=ax, color=COLOR_PALETTE)
    ax.set_title("Distribusi Rating Produk")
    return fig

def plot_top_categories(df: pd.DataFrame):
    """Plot 2: Top 10 Kategori"""
    fig, ax = plt.subplots(figsize=(6, 4))
    top_cat = df['Category'].value_counts().head(10).sort_values()
    top_cat.plot(kind='barh', color=COLOR_PALETTE, ax=ax)
    ax.set_title("Top 10 Product Categories")
    ax.set_xlabel("Jumlah Produk")
    return fig

def plot_review_count_distribution(df: pd.DataFrame):
    """Plot 3: Distribusi Jumlah Review"""
    fig, ax = plt.subplots(figsize=(6, 4))
    # Menggunakan log scale jika datanya sangat timpang, atau batasi range
    sns.histplot(df['ReviewCount'], bins=30, kde=True, ax=ax, color=COLOR_PALETTE)
    ax.set_title("Distribusi Jumlah Review")
    ax.set_xlabel("Review Count")
    return fig

def plot_correlation_heatmap(df: pd.DataFrame):
    """Plot 4: Korelasi Numerik"""
    fig, ax = plt.subplots(figsize=(6, 4))
    # Pastikan hanya kolom numerik
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df[['Rating', 'ReviewCount']].corr()
    
    sns.heatmap(corr, annot=True, cmap='Blues', ax=ax, fmt=".2f")
    ax.set_title("Korelasi Variabel Numerik")
    return fig