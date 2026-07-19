import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header
st.set_page_config(page_title="Tilapia Project Dashboard", layout="wide")
st.title("🐟 Red Tilapia 1000 Ekor / 150 Hari - eFishery Simulator")
st.markdown("Sistem simulasi tumbesaran ikan, keperluan dedak harian, dan anggaran FCR berdasarkan fasa ternakan.")

# 1. SIDEBAR INPUT CONTROLS
st.sidebar.header("🎯 Parameter Projek (Boleh Ubah)")
fish_count = st.sidebar.number_input("Bilangan Ikan (Ekor)", value=1000, step=100)
target_weight = st.sidebar.number_input("Target Berat Matang (gram)", value=350, step=10)
days_cycle = st.sidebar.number_input("Tempoh Ternakan (Hari)", value=150, step=5)

# 2. CALCULATION ENGINE
data = []
cumulative_feed = 0

# Variabel untuk kira total dedak mengikut fasa (untuk kira beg)
feed_pre_starter = 0
feed_starter = 0
feed_grower = 0
feed_finisher = 0

for d in range(1, int(days_cycle) + 1):
    # Linear growth math
    w = 2 + (target_weight - 2) * (d - 1) / (days_cycle - 1)
    bio = fish_count * w / 1000
    
    # --- LARASAN KADAR MAKAN & CARA LOGISTIK FEEDING ---
    if d <= 14: 
        fr = 7.0; typ = "Pre-starter"
        freq = "4 - 5 kali sehari (Sedikit demi sedikit, tekstur tepung/halus)"
    elif d <= 30: 
        fr = 5.0; typ = "Starter"
        freq = "3 - 4 kali sehari (Saiz pellet kecil 1mm - 2mm)"
    elif d <= 90: 
        fr = 2.8 if d > 60 else 3.8; typ = "Grower"
        freq = "2 - 3 kali sehari (Pagi, Tengahari, Petang - Saiz pellet 2mm - 3mm)"
    else: 
        fr = 1.5 if d <= 120 else 1.0; typ = "Finisher"
        freq = "2 kali sehari (Pagi & Lewat Petang - Saiz pellet 3mm - 4mm)"
        
    feed_day = bio * fr / 100
    cumulative_feed += feed_day
    
    # Kumpul berat dedak ikut fasa
    if typ == "Pre-starter": feed_pre_starter += feed_day
    elif typ == "Starter": feed_starter += feed_day
    elif typ == "Grower": feed_grower += feed_day
    elif typ == "Finisher": feed_finisher += feed_day
    
    # Formula FCR Akuakultur
    berat_awal_kolam = (fish_count * 2) / 1000
    kenaikan_berat_bersih = bio - berat_awal_kolam
    fcr_hari_ini = cumulative_feed / max(kenaikan_berat_bersih, 0.01)
    
    data.append({
        "Hari": d,
        "Berat Per Ekor (g)": round(w, 1),
        "Biomassa Total (kg)": round(bio, 1),
        "Feed Rate (%)": fr,
        "Dedak Harian (kg)": round(feed_day, 2),
        "Jenis Dedak": typ,
        "Kekerapan & Cara Pemberian": freq,
        "Projeksi FCR": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

# 3. TOP SUMMARY METRICS
st.subheader("📊 Rumusan Projek Baharu")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Jumlah Dedak Diperlukan", f"{round(cumulative_feed, 1)} kg")
with col2:
    st.metric("Anggaran FCR Akhir", f"{df['Projeksi FCR'].iloc[-1]}")
with col3:
    st.metric("Jumlah Biomassa Menuai", f"{df['Biomassa Total (kg)'].iloc[-1]} kg")
with col4:
    # Mengira jumlah keseluruhan beg (1 beg = 20kg)
    total_bags = math.ceil(cumulative_feed / 20)
    st.metric("Total Keperluan Dedak", f"{total_bags} Beg (20kg/beg)")

st.markdown("---")

# NEW SECTION: KIRAAN BEG IKUT JENIS
st.subheader("📦 Anggaran Pembelian Beg Dedak (Saiz Standard 20kg/Beg)")
st.markdown("*Nota: Kiraan telah dibundarkan ke atas (ceiling) untuk mengelakkan dedak tidak cukup di lapangan.*")

b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.info(f"**Pre-starter**\n\n{round(feed_pre_starter, 1)} kg\n\n➡️ **{math.ceil(feed_pre_starter / 20)} Beg**")
with b_col2:
    st.success(f"**Starter**\n\n{round(feed_starter, 1)} kg\n\n➡️ **{math.ceil(feed_starter / 20)} Beg**")
with b_col3:
    st.warning(f"**Grower**\n\n{round(feed_grower, 1)} kg\n\n➡️ **{math.ceil(feed_grower / 20)} Beg**")
with b_col4:
    st.error(f"**Finisher**\n\n{round(feed_finisher, 1)} kg\n\n➡️ **{math.ceil(feed_finisher / 20)} Beg**")

st.markdown("---")

# 4. INTERACTIVE VISUALIZATIONS
st.subheader("📈 Graf Keperluan Dedak Harian vs Pertumbuhan Ikan")
chart_data = df.set_index("Hari")[["Berat Per Ekor (g)", "Dedak Harian (kg)"]]
st.line_chart(chart_data)

# 5. LIVE DATA TABLE WITH FEEDING GUIDE
st.subheader("📋 Pelan Jadual Harian & Panduan Cara Memberi Makan")
st.dataframe(df, use_container_width=True, hide_index=True)

# 6. EXCEL DOWNLOAD BUTTON FOR EXPORTING
st.subheader("💾 Eksport Kembali")
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df)
st.download_button(
    label="Muat Turun Pelan Harian (CSV)",
    data=csv_data,
    file_name="Pelan_Harian_Tilapia.csv",
    mime="text/csv"
)
