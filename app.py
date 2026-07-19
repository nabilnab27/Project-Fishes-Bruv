import streamlit as st
import pandas as pd
import numpy as np

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

for d in range(1, int(days_cycle) + 1):
    # Linear growth math based on your openpyxl logic
    w = 2 + (target_weight - 2) * (d - 1) / (days_cycle - 1)
    bio = fish_count * w / 1000
    
    # Feeding Rate % and Type allocation based on days
    if d <= 14: 
        fr = 15.0; typ = "Pre-starter"
    elif d <= 30: 
        fr = 10.0; typ = "Starter"
    elif d <= 90: 
        fr = 4.0 if d > 60 else 6.0; typ = "Grower"
    else: 
        fr = 2.5 if d <= 120 else 1.2; typ = "Finisher"
        
    feed_day = bio * fr / 100
    cumulative_feed += feed_day
    
    # --- FORMULA FCR YANG DAH DIPATUHKAN (BETUL) ---
    berat_awal_kolam = (fish_count * 2) / 1000  # Benih 2 gram tukar ke kg
    kenaikan_berat_bersih = bio - berat_awal_kolam
    
    # Guna max(..., 0.01) supaya hari pertama tidak ralat (division by zero)
    fcr_hari_ini = cumulative_feed / max(kenaikan_berat_bersih, 0.01)
    
    data.append({
        "Hari": d,
        "Berat (g)": round(w, 1),
        "Biomassa (kg)": round(bio, 1),
        "Feed Rate (%)": fr,
        "Dedak Harian (kg)": round(feed_day, 2),
        "Jenis Dedak": typ,
        "Projeksi FCR": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

# 3. TOP SUMMARY METRICS
st.subheader("📊 Rumusan Projek Baharu")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Jumlah Dedak Diperlukan", f"{round(cumulative_feed, 1)} kg")
with col2:
    # Mengambil nilai FCR pada hari terakhir projek
    st.metric("Anggaran FCR Akhir", f"{df['Projeksi FCR'].iloc[-1]}")
with col3:
    st.metric("Jumlah Biomassa Menuai", f"{df['Biomassa (kg)'].iloc[-1]} kg")
with col4:
    st.metric("Fasa Dedak Terlibat", f"{df['Jenis Dedak'].nunique()} Jenis")

st.markdown("---")

# 4. INTERACTIVE VISUALIZATIONS
st.subheader("📈 Graf Keperluan Dedak Harian vs Pertumbuhan Ikan")

# Structuring chart data cleanly
chart_data = df.set_index("Hari")[["Berat (g)", "Dedak Harian (kg)"]]
st.line_chart(chart_data)

# 5. LIVE DATA TABLE 
st.subheader("📋 Pelan Harian Lengkap (150 Hari)")
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
