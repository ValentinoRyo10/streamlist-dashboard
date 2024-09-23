import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Customer Behavior Dashboard & RFM Analysis")
st.write("")
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/main_data.csv')
    return data

data = load_data()

st.sidebar.header("User Input")
analysis_type = st.sidebar.selectbox("Pilih Analisis", ["RFM Analysis", "Product Analysis", "Customer Analysis"])


def rfm_analysis(data):
    snapshot_date = pd.to_datetime('2024-09-23')

    rfm_data = data.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - pd.to_datetime(x).max()).days, 
        'order_id': 'nunique',  
        'total_cost': 'sum' 
    }).reset_index()

    rfm_data.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

    rfm_data['R_Score'] = pd.qcut(rfm_data['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm_data['F_Score'] = pd.qcut(rfm_data['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_data['M_Score'] = pd.qcut(rfm_data['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

    rfm_data['RFM_Segment'] = rfm_data['R_Score'].astype(str) + rfm_data['F_Score'].astype(str) + rfm_data['M_Score'].astype(str)
    rfm_data['RFM_Score'] = rfm_data[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    st.write("### RFM Data:")
    st.dataframe(rfm_data)

    st.write("### Distribusi RFM Score Pelanggan")
    plt.figure(figsize=(10, 6))
    plt.hist(rfm_data['RFM_Score'], bins=10, color='skyblue', edgecolor='black')
    plt.title('Distribusi Skor RFM Pelanggan', fontweight='bold')
    plt.xlabel('RFM Score')
    plt.ylabel('Jumlah Pelanggan')
    st.pyplot(plt)

def product_analysis(data):
    st.write("### Top 10 produk yang memiliki tingkat pembelian tertinggi")
    all_data_df = pd.read_csv("dashboard/main_data.csv")
    top_products = all_data_df.groupby('product_category_name')['order_id'].nunique().reset_index()
    top_products.columns = ['product_category_name', 'purchase_count']
    top_10_products = top_products.sort_values(by='purchase_count', ascending=False).head(10)
    top_10_products.reset_index(drop=True, inplace=True)
    top_10_products

    wilayah_mayoritas = all_data_df.groupby('product_category_name')['customer_state'].agg(lambda x: x.mode()[0]).reset_index()
    wilayah_mayoritas.columns = ['product_category_name', 'majority_customer_state']

    kota_mayoritas = all_data_df.groupby('product_category_name')['customer_city'].agg(lambda x: x.mode()[0]).reset_index()
    kota_mayoritas.columns = ['product_category_name', 'majority_customer_city']

    result = pd.merge(top_10_products, wilayah_mayoritas, on='product_category_name')
    result = pd.merge(result, kota_mayoritas, on='product_category_name')
    result.reset_index(drop=True, inplace=True)

    rata_rata_berat = all_data_df['product_weight_g'].mean()
    rata_rata_volume = all_data_df['product_volume_cm3'].mean()

    average_weight_volume = all_data_df.groupby('product_category_name').agg(
    average_weight=('product_weight_g', 'mean'),
    average_volume=('product_volume_cm3', 'mean')
    ).reset_index()

    result = pd.merge(result, average_weight_volume, on='product_category_name')

    result.reset_index(drop=True, inplace=True)

    categories = result['product_category_name']
    purchase_counts = result['purchase_count']

    plt.figure(figsize=(12, 6))
    bars = plt.barh(categories, purchase_counts, color='skyblue')
    plt.xlabel('Jumlah Pembelian')
    plt.title('Top 10 Kategori Produk dengan Pembelian Tertinggi', fontweight="bold")
    plt.grid(axis='x')


    for bar in bars:
        plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f'{int(bar.get_width())}', va='center')

    st.pyplot(plt)
    st.write("")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("### Rata-rata berat dan volume pada top 10 produk pembelian tertinggi dan perbandingannya dengan rata-rata ukuran keseluruhan produk")

    rata_rata_berat = all_data_df['product_weight_g'].mean()
    rata_rata_volume = all_data_df['product_volume_cm3'].mean()

    st.write(f"Rata-rata Berat Total Produk : {rata_rata_berat} g")
    st.write(f"Rata-rata Volume Total Produk : {rata_rata_volume} cm³")

    result

    weights = result['average_weight']
    volumes = result['average_volume']

    fig, ax1 = plt.subplots(figsize=(12, 6))

    bar_width = 0.4
    x = np.arange(len(result['product_category_name']))

    bars_weight = ax1.bar(x, weights, width=bar_width, label='rata-rata berat (gr)', color='skyblue')

    ax2 = ax1.twinx()
    bars_volume = ax2.bar(x + bar_width, volumes, width=bar_width, label='rata-rata volume (cm^3)', color='pink')

    ax1.axhline(rata_rata_berat, color='blue', linestyle='--', label='rata-rata berat total produk')
    ax2.axhline(rata_rata_volume, color='red', linestyle='--', label='rata-rata volume total produk')

    ax1.set_xlabel('Kategori Produk')
    ax1.set_ylabel('Rata-rata Berat (gr)')
    ax2.set_ylabel('Rata-rata Volume (cm^3)')
    ax1.set_title('Rata-rata Berat dan Volume Top 10 Produk dengan Pembelian Tertinggi', fontweight='bold')
    ax1.set_xticks(x + bar_width / 2)
    ax1.set_xticklabels(result['product_category_name'], rotation=45)

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    st.pyplot(plt)
    st.write("")

def customer_analysis(data):
    st.write("### Top 10 rata-rata waktu pengiriman tiap kota customers")
    all_data_df = pd.read_csv("dashboard/main_data.csv")
    avg_delivery_time_per_city = all_data_df.groupby('customer_city')['delivery_time (day)'].mean().reset_index()
    avg_delivery_time_per_city.columns = ['customer_city', 'avg_delivery_time']
    avg_delivery_time_per_city = avg_delivery_time_per_city.sort_values(by='avg_delivery_time', ascending=False).head(10).reset_index(drop=True)
    avg_delivery_time_per_city
    st.write("")
    top_10_avg_delivery_time_per_city = avg_delivery_time_per_city.sort_values(by='avg_delivery_time', ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(top_10_avg_delivery_time_per_city['customer_city'], top_10_avg_delivery_time_per_city['avg_delivery_time'], color='skyblue')
    plt.xlabel('Kota Customer')
    plt.ylabel('Rata-rata Waktu Pengiriman (hari)')
    plt.title('Top 10 Rata-rata Waktu Pengiriman berdasarkan Kota Customers', fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    for index, value in enumerate(top_10_avg_delivery_time_per_city['avg_delivery_time']):
        plt.text(index, value, f'{value:.2f}', ha='center', va='bottom')

    st.pyplot(plt)
    st.write("")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("### Top 10 rata-rata waktu pengiriman tiap state customers")
    avg_delivery_time_per_state = all_data_df.groupby('customer_state')['delivery_time (day)'].mean().reset_index()
    avg_delivery_time_per_state.columns = ['customer_state', 'avg_delivery_time']
    avg_delivery_time_per_state = avg_delivery_time_per_state.sort_values(by='avg_delivery_time', ascending=False).head(10).reset_index(drop=True)
    avg_delivery_time_per_state
    st.write("")
    st.write("### Dengan informasi jumlah penjualan (sales count) : ")
    penjualan_tiap_wilayah = all_data_df.groupby('customer_state')['order_id'].nunique().reset_index()
    penjualan_tiap_wilayah.columns = ['customer_state', 'sales_count']

    state_analysis = pd.merge(avg_delivery_time_per_state, penjualan_tiap_wilayah, on='customer_state')
    state_analysis = state_analysis.head(10)
    state_analysis
    st.write("")
    plt.figure(figsize=(12, 6))
    plt.scatter(state_analysis['sales_count'], state_analysis['avg_delivery_time'], color='blue')
    plt.xlabel('Jumlah Pembelian (order)')
    plt.ylabel('Rata-rata Waktu Pengiriman (hari)')
    plt.title('Hubungan Jumlah Pembelian dan Rata-rata Waktu Pengiriman', fontweight='bold')
    st.pyplot(plt)
if analysis_type == 'RFM Analysis':
    rfm_analysis(data)
elif analysis_type == 'Product Analysis':
    product_analysis(data)
elif analysis_type == "Customer Analysis":
    customer_analysis(data)
