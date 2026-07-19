import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header
st.set_page_config(page_title="Tilapia Project Dashboard", layout="wide")
st.title("🐟 Red Tilapia eFishery Simulator & Budget Tracker")
st.markdown("Sistem simulasi tumbesaran ikan, keperluan dedak, kos Cargill, dan modal pembelian benih live Malaysia.")

# Data mapping untuk saiz inci -> berat (g) dan harga anggaran pasaran (RM)
size_options = {
    "1.5 Inci": {"weight": 1.2, "price": 0.18},
    "2.0 Inci": {"weight": 2.5, "price": 0.25},
    "2.5 Inci": {"weight": 4.5, "price": 0.35},
    "3.0 Inci": {"weight": 8.0, "price": 0.45},
    "3.5 Inci": {"weight": 13.0, "price": 0.55},
    "4.0 Inci": {"weight": 22.0, "price": 0.65},
    "4.5 Inci": {"weight": 32.0, "price": 0.75},
    "5.0 Inci": {"weight": 48.0, "price": 0.90}
}

# 1. SIDEBAR INPUT CONTROLS
st.sidebar.header("🎯 Parameter Projek (Boleh Ubah)")
fish_count = st.sidebar.number_input("Bilangan Ikan (Ekor)", value=1000, step=100)

# Dropdown untuk memilih saiz inci starting ikan
selected_size = st.sidebar.selectbox("Saiz Mula Benih Ikan (Inci)", list(size_options.keys()), index=1) # Default 2.0 inci
initial_weight = size_options[selected_size]["weight"]
default_seed_price = size_options[selected_size]["price"]

# Input harga benih seekor secara live
seed_price_input = st.sidebar.number_input(f"Harga Benih Seekor ({selected_size}) (RM)", value=default_seed_price, step=0.05)

target_weight = st.sidebar.number_input("Target Berat Matang (gram)", value=350, step=10)
days_cycle = st.sidebar.number_input("Tempoh Ternakan (Hari)", value=150, step=5)

# 2. INPUT HARGA DEDAK IKUT KEDAI USER
st.sidebar.header("💰 Harga Beg Cargill 20kg Kedai Anda (RM)")
price_pre = st.sidebar.number_input("Harga Pre-starter", value=90.0, step=5.0)
price_star = st.sidebar.number_input("Harga Starter", value=71.0, step=5.0)
price_grow = st.sidebar.number_input("Harga Grower", value=70.0, step=5.0)
price_fin = st.sidebar.number_input("Harga Finisher", value=70.0, step=5.0)

# 3. CALCULATION ENGINE
data = []
cumulative_feed = 0

feed_pre_starter = 0
feed_starter = 0
feed_grower = 0
feed_finisher = 0

for d in range(1, int(days_cycle) + 1):
    # Linear growth math bermula dari berat awal pilihan saiz inci
    w = initial_weight + (target_weight - initial_weight) * (d - 1) / (days_cycle - 1)
    bio = fish_count * w / 1000
    
    # Penentuan fasa mengikut tetapan hari & kadar makan standard industri
    if d <= 14: 
        fr = 7.0; typ = "Pre-starter"
        freq = "4 - 5 kali sehari (Tekstur tepung/halus)"
        p_price = price_pre
    elif d <= 30: 
        fr = 5.0; typ = "Starter"
        freq = "3 - 4 kali sehari (Pellet kecil 1mm - 2mm)"
        p_price = price_star
    elif d <= 90: 
        fr = 2.8 if d > 60 else 3.8; typ = "Grower"
        freq = "2 - 3 kali sehari (Pellet sederhana 2mm - 3mm)"
        p_price = price_grow
    else: 
        fr = 1.5 if d <= 120 else 1.0; typ = "Finisher"
        freq = "2 kali sehari (Pellet matang 3mm - 4mm)"
        p_price = price_fin
        
    feed_day = bio * fr / 100
    cumulative_feed += feed_day
    
    # Kumpul berat dedak ikut fasa
    if typ == "Pre-starter": feed_pre_starter += feed_day
    elif typ == "Starter": feed_starter += feed_day
    elif typ == "Grower": feed_grower += feed_day
    elif typ == "Finisher": feed_finisher += feed_day
    
    # Formula FCR Akuakultur
    berat_awal_kolam = (fish_count * initial_weight) / 1000
    kenaikan_berat_bersih = bio - berat_awal_kolam
    fcr_hari_ini = cumulative_feed / max(kenaikan_berat_bersih, 0.01)
    
    # Kira kos dedak harian
    cost_day = feed_day * (p_price / 20)
    
    data.append({
        "Hari": d,
        "Berat Per Ekor (g)": round(w, 1),
        "Biomassa Total (kg)": round(bio, 1),
        "Feed Rate (%)": fr,
        "Dedak Harian (kg)": round(feed_day, 2),
        "Kos Harian (RM)": round(cost_day, 2),
        "Jenis Dedak": typ,
        "Kekerapan & Cara Pemberian": freq,
        "Projeksi FCR": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

# Kira jumlah beg sebenar (bundar ke atas)
bags_pre = math.ceil(feed_pre_starter / 20)
bags_star = math.ceil(feed_starter / 20)
bags_grow = math.ceil(feed_grower / 20)
bags_fin = math.ceil(feed_finisher / 20)

# Jumlah kos dedak dan kos benih ikan
total_feed_cost = (bags_pre * price_pre) + (bags_star * price_star) + (bags_grow * price_grow) + (bags_fin * price_fin)
total_seed_cost = fish_count * seed_price_input
grand_total_cost = total_feed_cost + total_seed_cost

# 4. TOP SUMMARY METRICS
st.subheader(f"📊 Rumusan Projek (Hari 1 - {int(days_cycle)} | Benih {selected_size})")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Kos Benih Ikan", f"RM {round(total_seed_cost, 2)}")
with col2:
    st.metric("Total Kos Dedak (Kedai Anda)", f"RM {round(total_feed_cost, 2)}")
with col3:
    st.metric("Jumlah Modal Asas Bersih", f"RM {round(grand_total_cost, 2)}")
with col4:
    st.metric("Anggaran FCR Akhir", f"{df['Projeksi FCR'].iloc[-1]}")

st.markdown("---")

# SECTION: KIRAAN BEG DAN KOS IKUT HARGA KEDAI USER
st.subheader("📦 Anggaran Pembelian & Kos Dedak Siri Cargill Aqua Focus (20kg/Beg)")
st.markdown(f"*Nota: Menggunakan spesifikasi berat permulaan benih **{initial_weight} gram** berdasarkan pilihan saiz **{selected_size}**.*")

b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.info(f"**Pre-starter**\n\nBerat: {round(feed_pre_starter, 1)} kg\n\n➡️ **{bags_pre} Beg** (RM {bags_pre * price_pre:.2f})")
with b_col2:
    st.success(f"**Starter**\n\nBerat: {round(feed_starter, 1)} kg\n\n➡️ **{bags_star} Beg** (RM {bags_star * price_star:.2f})")
with b_col3:
    st.warning(f"**Grower**\n\nBerat: {round(feed_grower, 1)} kg\n\n➡️ **{bags_grow} Beg** (RM {bags_grow * price_grow:.2f})")
with b_col4:
    st.error(f"**Finisher**\n\nBerat: {round(feed_finisher, 1)} kg\n\n➡️ **{bags_fin} Beg** (RM {bags_fin * price_fin:.2f})")

st.markdown("---")

# 5. INTERACTIVE VISUALIZATIONS
st.subheader("📈 Graf Keperluan Dedak Harian vs Pertumbuhan Ikan")
chart_data = df.set_index("Hari")[["Berat Per Ekor (g)", "Dedak Harian (kg)"]]
st.line_chart(chart_data)

# 6. LIVE DATA TABLE WITH FEEDING GUIDE
st.subheader("📋 Pelan Jadual Harian, Kos RM & Panduan Cara Memberi Makan")
st.dataframe(df, use_container_width=True, hide_index=True)

# 7. EXCEL DOWNLOAD BUTTON FOR EXPORTING
st.subheader("💾 Eksport Kembali")
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df)
st.download_button(
    label="Muat Turun Pelan Harian (CSV)",
    data=csv_data,
    file_name="Pelan_Harian_Tilapia_Lengkap.csv",
    mime="text/csv"
)
