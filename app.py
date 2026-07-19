import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header
st.set_page_config(page_title="eFishery Smart Tilapia ERP", layout="wide")
st.title("🐟 eFishery Smart Tilapia Farm ERP & Budget Tracker")
st.markdown("Sistem Pengurusan Pintar Akuakultur: Simulasi Tumbesaran, Kawalan Makanan, Pengurusan Kualiti Air, Risiko Kematian, dan Unjuran Untung Bersih Ladang.")

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
st.sidebar.header("🎯 1. Parameter Utama Projek")
fish_count_input = st.sidebar.number_input("Bilangan Benih Dibeli (Ekor)", value=1000, step=100)

selected_size = st.sidebar.selectbox("Saiz Mula Benih Ikan (Inci)", list(size_options.keys()), index=1)
initial_weight = size_options[selected_size]["weight"]
default_seed_price = size_options[selected_size]["price"]

seed_price_input = st.sidebar.number_input(f"Harga Benih Seekor ({selected_size}) (RM)", value=default_seed_price, step=0.05)
target_weight = st.sidebar.number_input("Target Berat Matang Tuan (gram)", value=350, step=10)
days_cycle = st.sidebar.number_input("Tempoh Ternakan (Hari)", value=150, step=5)

st.sidebar.header("⚠️ 2. Manajemen Risiko")
survival_rate = st.sidebar.slider("Kadar Hidup Ikan / Survival Rate (%)", min_value=50, max_value=100, value=85, step=5)

st.sidebar.header("💰 3. Ekonomi & Pasaran Semasa")
price_pre = st.sidebar.number_input("Harga Beg Pre-starter 20kg (RM)", value=90.0, step=5.0)
price_star = st.sidebar.number_input("Harga Beg Starter 20kg (RM)", value=71.0, step=5.0)
price_grow = st.sidebar.number_input("Harga Beg Grower 20kg (RM)", value=70.0, step=5.0)
price_fin = st.sidebar.number_input("Harga Beg Finisher 20kg (RM)", value=70.0, step=5.0)

selling_price_per_kg = st.sidebar.number_input("Harga Jualan Tilapia Merah Pasaran Live (RM/KG)", value=14.0, step=0.5)

# 2. CALCULATION ENGINE WITH MORTALITY & ECONOMICS
data = []
cumulative_feed = 0

feed_pre_starter = 0
feed_starter = 0
feed_grower = 0
feed_finisher = 0

# Kiraan kadar kematian harian secara linear untuk simulasi realistik
total_mortality_pct = 100 - survival_rate

for d in range(1, int(days_cycle) + 1):
    # Bilangan ikan menyusut secara berperingkat sepanjang kitaran akibat mortality rate
    current_fish_count = fish_count_input - (fish_count_input * (total_mortality_pct / 100) * (d - 1) / (days_cycle - 1))
    
    # Linear growth math
    w = initial_weight + (target_weight - initial_weight) * (d - 1) / (days_cycle - 1)
    bio = current_fish_count * w / 1000
    
    # Penentuan fasa dedak dan cara makan
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
    
    if typ == "Pre-starter": feed_pre_starter += feed_day
    elif typ == "Starter": feed_starter += feed_day
    elif typ == "Grower": feed_grower += feed_day
    elif typ == "Finisher": feed_finisher += feed_day
    
    # Formula FCR Akuakultur Bersih
    berat_awal_kolam = (fish_count_input * initial_weight) / 1000
    kenaikan_berat_bersih = bio - berat_awal_kolam
    fcr_hari_ini = cumulative_feed / max(kenaikan_berat_bersih, 0.01)
    
    # Kira kos dedak harian
    cost_day = feed_day * (p_price / 20)
    
    # Jadual Pensampelan (Sampling Guide) - Setiap 30 hari sekali
    sampling_status = "⚠️ Ambil Sampel Timbang!" if d % 30 == 0 or d == 1 else "Pantau Air"
    
    data.append({
        "Hari": d,
        "Ikan Hidup (Ekor)": int(current_fish_count),
        "Berat Per Ekor (g)": round(w, 1),
        "Biomassa Total (kg)": round(bio, 1),
        "Feed Rate (%)": fr,
        "Dedak Harian (kg)": round(feed_day, 2),
        "Kos Harian (RM)": round(cost_day, 2),
        "Jenis Dedak": typ,
        "Kekerapan & Cara": freq,
        "Panduan Praktikal": sampling_status,
        "Projeksi FCR": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

# Kira logistik beg dedak
bags_pre = math.ceil(feed_pre_starter / 20)
bags_star = math.ceil(feed_starter / 20)
bags_grow = math.ceil(feed_grower / 20)
bags_fin = math.ceil(feed_finisher / 20)

total_feed_cost = (bags_pre * price_pre) + (bags_star * price_star) + (bags_grow * price_grow) + (bags_fin * price_fin)
total_seed_cost = fish_count_input * seed_price_input
grand_total_cost = total_feed_cost + total_seed_cost

# Kiraan Hasil Tuaian Kasar & Untung Bersih Ladang
final_biomass = df["Biomassa Total (kg)"].iloc[-1]
gross_revenue = final_biomass * selling_price_per_kg
net_profit = gross_revenue - grand_total_cost

# 3. TOP SUMMARY METRICS (FINANCIAL & PRODUCTION)
st.subheader("💰 Ringkasan Analisis Kewangan Ladang")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Jumlah Modal Kasar (Ikan + Dedak)", f"RM {grand_total_cost:.2f}")
with m_col2:
    st.metric("Anggaran Hasil Jualan Kasar", f"RM {gross_revenue:.2f}")
with m_col3:
    if net_profit >= 0:
        st.metric("🔥 Anggaran Untung Bersih", f"RM {net_profit:.2f}")
    else:
        st.metric("🚨 Anggaran Rugi Bersih", f"RM {net_profit:.2f}")
with m_col4:
    st.metric("Anggaran FCR Akhir Projek", f"{df['Projeksi FCR'].iloc[-1]}")

# 4. WATER QUALITY BAR & LOGISTICS
st.markdown("---")
st.subheader("💧 1. Parameter Kualiti Air Optimum (Penting untuk Kekalkan FCR)")
w_col1, w_col2, w_col3 = st.columns(3)
w_col1.success("**Suhu Air Ideal:**\n\n28°C - 32°C\n\n*(Metabolisme ikan aktif)*")
w_col2.success("**Nilai pH Kolam:**\n\n6.5 - 8.5\n\n*(Elak ikan stres & penyakit)*")
w_col3.success("**Oksigen Terlarut (DO):**\n\n> 4.0 mg/L\n\n*(Pasang kincir air waktu malam)*")

st.markdown("---")

# SECTION: KIRAAN BEG DAN KOS IKUT HARGA KEDAI USER
st.subheader("📦 2. Logistik Anggaran Pembelian & Pecahan Beg Dedak (20kg/Beg)")
st.markdown(f"*Nota: Simulasi mengira keperluan dedak berdasarkan baki ikan hidup dengan target kadar kelangsungan hidup sebanyak **{survival_rate}%**.*")

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
st.subheader("📈 3. Graf Tumbesaran Biomassa vs Dedak Harian (kg)")
chart_data = df.set_index("Hari")[["Biomassa Total (kg)", "Dedak Harian (kg)"]]
st.line_chart(chart_data)

# 6. LIVE DATA TABLE WITH MORTALITY & SAMPLING GUIDE
st.subheader("📋 4. Pelan Lengkap Operasi Harian Ladang")
st.dataframe(df, use_container_width=True, hide_index=True)

# 7. EXCEL DOWNLOAD BUTTON FOR EXPORTING
st.subheader("💾 5. Eksport Pelan Logistik Ladang")
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df)
st.download_button(
    label="Muat Turun Pelan Harian Komprehensif (CSV)",
    data=csv_data,
    file_name="Pelan_Operasi_Tilapia_Lengkap.csv",
    mime="text/csv"
)
