import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header & premium layout
st.set_page_config(page_title="Nabils Fish System", layout="wide", page_icon="🐟")

# CUSTOM CSS FOR PREMIUM LOOK
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1E88E5;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 500;
        color: #555555;
    }
    </style>
""", unsafe_allow_html=True)

# NAMA TAJUK BARU BARU: NABILS FISH SYSTEM
st.title("✨ 🐟 Nabils Fish System v2.5 ✨")
st.markdown("### *Sistem Pengurusan Pintar Akuakultur & Unjuran Kewangan Ladang Komersial*")
st.markdown("---")

# Data mapping untuk saiz inci -> berat (g) dan harga anggaran pasaran (RM)
size_options = {
    "1.5 Inci 📏": {"weight": 1.2, "price": 0.18},
    "2.0 Inci 📏": {"weight": 2.5, "price": 0.25},
    "2.5 Inci 📏": {"weight": 4.5, "price": 0.35},
    "3.0 Inci 📏": {"weight": 8.0, "price": 0.45},
    "3.5 Inci 📏": {"weight": 13.0, "price": 0.55},
    "4.0 Inci 📏": {"weight": 22.0, "price": 0.65},
    "4.5 Inci 📏": {"weight": 32.0, "price": 0.75},
    "5.0 Inci 📏": {"weight": 48.0, "price": 0.90}
}

# Data mapping untuk Jenis Kolam -> Kesan Baseline FCR & Nota Khas
pond_options = {
    "🧱 Kolam Simen (Air Bukit/Sistem Aliran)": {
        "fcr_mod": 0.05, 
        "tips": "⚠️ Kolam simen tiada makanan semula jadi (plankton). Sisa makanan mudah mendap di dasar. Wajib pasang sistem buang najis tengah (central drain) atau buat sifon dasar setiap minggu untuk mengelakkan gas amonia toksik naik.",
        "aerator_rec": "Sangat sesuai menggunakan Ring Blower (cth: 370W) dipadankan dengan tiub buih halus (Aero-Tube/Uniring) di dasar."
    },
    "🪵 Kolam Tanah Tradisional": {
        "fcr_mod": -0.10, 
        "tips": "🍀 Kolam tanah kaya dengan plankton dan lumut sebagai snek tambahan ikan (FCR lebih jimat). Namun, air mudah keruh selepas hujan lebat. Wajib tabur kapur pertanian (Dolomite) secara berkala untuk menstabilkan pH air kolam.",
        "aerator_rec": "Lebih sesuai menggunakan Kincir Air (Paddle Wheel) untuk menolak air dan mengudarakan kawasan permukaan kolam yang luas."
    },
    "⛺ Kolam Kanvas / Tangki HDPE": {
        "fcr_mod": 0.00, 
        "tips": "📱 Sistem tangki kanvas memudahkan pengurusan greding saiz ikan dan pembersihan. Risiko kebocoran dinding kolam harus dipantau. Pastikan tiada bucu tajam di dalam kolam yang boleh mencederakan badan ikan Tilapia Merah.",
        "aerator_rec": "Wajib menggunakan peranti pengudaraan berterusan (Ring Blower atau Root Blower) dengan sistem sandaran (backup) elektrik."
    },
    "🧬 Sistem Biofloc (Bakteria Baik)": {
        "fcr_mod": -0.20, 
        "tips": "🧬 Teknologi Biofloc menukarkan sisa amonia najis ikan menjadi gumpalan protein (floc) untuk dimakan semula oleh ikan. FCR paling rendah dan jimat dedak. Syarat utama: Pengawal pH, sumber karbon (molases/gula merah) & C:N ratio wajib dijaga rapi.",
        "aerator_rec": "Oksigen Terlarut (DO) WAJIB sentiasa > 5.0 mg/L sepanjang masa. Kegagalan aerator selama 2 jam boleh menyebabkan kematian mengejut seluruh kolam."
    }
}

# 1. SIDEBAR INPUT CONTROLS
st.sidebar.header("⚙️ 1. Parameter Utama Projek")
fish_count_input = st.sidebar.number_input("Bilangan Benih Dibeli (Ekor)", value=1000, step=100)

selected_size = st.sidebar.selectbox("Saiz Mula Benih Ikan", list(size_options.keys()), index=1)
initial_weight = size_options[selected_size]["weight"]
default_seed_price = size_options[selected_size]["price"]
seed_price_input = st.sidebar.number_input(f"Harga Benih Seekor (RM)", value=default_seed_price, step=0.05)

selected_pond = st.sidebar.selectbox("Jenis Kolam Ternakan", list(pond_options.keys()), index=0)
fcr_modifier = pond_options[selected_pond]["fcr_mod"]

target_weight = st.sidebar.number_input("Target Berat Matang (gram)", value=350, step=10)
days_cycle = st.sidebar.number_input("Tempoh Ternakan (Hari)", value=150, step=5)

st.sidebar.header("🛡️ 2. Manajemen Risiko")
survival_rate = st.sidebar.slider("Kadar Hidup Ikan / Survival Rate (%)", min_value=50, max_value=100, value=85, step=5)

st.sidebar.header("💵 3. Kos Beg Cargill 20kg (RM)")
price_pre = st.sidebar.number_input("Harga Pre-starter", value=90.0, step=5.0)
price_star = st.sidebar.number_input("Harga Starter", value=71.0, step=5.0)
price_grow = st.sidebar.number_input("Harga Grower", value=70.0, step=5.0)
price_fin = st.sidebar.number_input("Harga Finisher", value=70.0, step=5.0)

st.sidebar.header("🏪 4. Harga Pasaran Tuaian")
selling_price_per_kg = st.sidebar.number_input("Harga Jualan Live (RM/KG)", value=14.0, step=0.5)

# INTERACTIVE ADDITIONAL COSTS INPUT IN MAIN PANEL
st.subheader("⚡ 🔌 Kos Operasi Tambahan (Boleh Ditambah/Edit Live)")
st.markdown("💡 *Klik pada baris kosong di bawah atau tekan butang **➕ Add row** untuk menambah kos seperti Elektrik, Perubatan/Ubat, Air Bukit, Gaji Pekerja dll.*")

# Initialize default rows for Additional Costs
if 'additional_costs' not in st.session_state:
    st.session_state.additional_costs = pd.DataFrame([
        {"Jenis Perbelanjaan": "Bil Elektrik (Pam Aerator HG-370)", "Jumlah Kos Keseluruhan Projek (RM)": 150.00},
        {"Jenis Perbelanjaan": "Perubatan & Vitamin Ikan (Garam/Kapur)", "Jumlah Kos Keseluruhan Projek (RM)": 50.00}
    ])

# Render dynamic data editor grid
edited_costs_df = st.data_editor(
    st.session_state.additional_costs,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Jenis Perbelanjaan": st.column_config.TextColumn("Jenis Perbelanjaan (Sila taip di sini)", help="Contoh: Elektrik, Ubat, Bil Air, Gaji"),
        "Jumlah Kos Keseluruhan Projek (RM)": st.column_config.NumberColumn("Jumlah Kos (RM)", format="RM %.2f", min_value=0.0)
    }
)
st.session_state.additional_costs = edited_costs_df

# Calculate total additional costs safely
total_additional_cost = edited_costs_df["Jumlah Kos Keseluruhan Projek (RM)"].sum()

# 2. CALCULATION ENGINE
data = []
cumulative_feed = 0

feed_pre_starter = 0
feed_starter = 0
feed_grower = 0
feed_finisher = 0

total_mortality_pct = 100 - survival_rate

for d in range(1, int(days_cycle) + 1):
    current_fish_count = fish_count_input - (fish_count_input * (total_mortality_pct / 100) * (d - 1) / (days_cycle - 1))
    w = initial_weight + (target_weight - initial_weight) * (d - 1) / (days_cycle - 1)
    bio = current_fish_count * w / 1000
    
    if d <= 14: 
        fr = 7.0; typ = "🍼 Pre-starter"
        freq = "4 - 5 kali sehari (Tepung/Halus)"
        p_price = price_pre
    elif d <= 30: 
        fr = 5.0; typ = "🌱 Starter"
        freq = "3 - 4 kali sehari (Pellet 1mm - 2mm)"
        p_price = price_star
    elif d <= 90: 
        fr = 2.8 if d > 60 else 3.8; typ = "🥦 Grower"
        freq = "2 - 3 kali sehari (Pellet 2mm - 3mm)"
        p_price = price_grow
    else: 
        fr = 1.5 if d <= 120 else 1.0; typ = "🍖 Finisher"
        freq = "2 kali sehari (Pellet 3mm - 4mm)"
        p_price = price_fin
        
    adjusted_fr = max(fr + (fcr_modifier * 2), 0.5)
    feed_day = bio * adjusted_fr / 100
    cumulative_feed += feed_day
    
    if "Pre-starter" in typ: feed_pre_starter += feed_day
    elif "Starter" in typ: feed_starter += feed_day
    elif "Grower" in typ: feed_grower += feed_day
    elif "Finisher" in typ: feed_finisher += feed_day
    
    berat_awal_kolam = (fish_count_input * initial_weight) / 1000
    kenaikan_berat_bersih = bio - berat_awal_kolam
    
    fcr_hari_ini = (cumulative_feed / max(kenaikan_berat_bersih, 0.01)) + (fcr_modifier * (d / days_cycle))
    cost_day = feed_day * (p_price / 20)
    sampling_status = "⚠️ Timbang Sampel!" if d % 30 == 0 or d == 1 else "👍 Selamat"
    
    data.append({
        "Hari": d,
        "Ikan Hidup (Ekor)": int(current_fish_count),
        "Berat Per Ekor (g)": round(w, 1),
        "Biomassa Total (kg)": round(bio, 1),
        "Feed Rate (%)": round(adjusted_fr, 2),
        "Dedak Harian (kg)": round(feed_day, 2),
        "Kos Harian (RM)": round(cost_day, 2),
        "Jenis Dedak": typ,
        "Kekerapan & Cara": freq,
        "Status Operasi": sampling_status,
        "Projeksi FCR": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

bags_pre = math.ceil(feed_pre_starter / 20)
bags_star = math.ceil(feed_starter / 20)
bags_grow = math.ceil(feed_grower / 20)
bags_fin = math.ceil(feed_finisher / 20)

total_feed_cost = (bags_pre * price_pre) + (bags_star * price_star) + (bags_grow * price_grow) + (bags_fin * price_fin)
total_seed_cost = fish_count_input * seed_price_input

grand_total_cost = total_feed_cost + total_seed_cost + total_additional_cost

final_biomass = df["Biomassa Total (kg)"].iloc[-1]
gross_revenue = final_biomass * selling_price_per_kg
net_profit = gross_revenue - grand_total_cost

st.markdown("---")

# 3. TOP SUMMARY METRICS
st.subheader("💰 Ringkasan Analisis Kewangan Ladang (Real-Time)")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("💵 Total Modal Kasar Keseluruhan", f"RM {grand_total_cost:.2f}", help="Termasuk benih, dedak dan kos tambahan")
with m_col2:
    st.metric("📈 Hasil Jualan Kasar", f"RM {gross_revenue:.2f}")
with m_col3:
    if net_profit >= 0:
        st.metric("🔥 UNTUNG BERSIH MUTLAK", f"RM {net_profit:.2f}", delta=f"Cuan Bersih")
    else:
        st.metric("🚨 RUGI BERSIH MUTLAK", f"RM {net_profit:.2f}", delta=f"Rugi Kos", delta_color="inverse")
with m_col4:
    st.metric("📊 Jangkaan FCR Akhir", f"{df['Projeksi FCR'].iloc[-1]}")

st.markdown("---")

# PREMIUM CHARTS
st.subheader("📈 Visualisasi Unjuran Projeksi Ladang (Lebih Mudah Difahami)")
g_col1, g_col2 = st.columns(2)
with g_col1:
    st.markdown("#### **1. Graf Tumbesaran Berat Ikan vs Keperluan Dedak Harian (kg)**")
    chart_data1 = df.set_index("Hari")[["Berat Per Ekor (g)", "Dedak Harian (kg)"]]
    st.area_chart(chart_data1)
with g_col2:
    st.markdown("#### **2. Graf Akumulasi Total Biomassa Kolam (kg) & Trend FCR**")
    chart_data2 = df.set_index("Hari")[["Biomassa Total (kg)", "Projeksi FCR"]]
    st.line_chart(chart_data2)

st.markdown("---")

# PANDUAN LAPANGAN DINAMIK
st.subheader(f"🛠️ Panduan & Diagnosis Lapangan: {selected_pond}")
t_col1, t_col2 = st.columns(2)
with t_col1:
    st.info(f"**💡 Info & Tips Pengurusan Sisa/Air:**\n\n{pond_options[selected_pond]['tips']}")
with t_col2:
    st.warning(f"**💨 Cadangan Pemasangan Sistem Aerator (Oksigen):**\n\n{pond_options[selected_pond]['aerator_rec']}")

st.markdown("---")

# WATER QUALITY GUIDELINES
st.subheader("💧 Parameter Kualiti Air Optimum (Penting untuk Kekalkan FCR)")
w_col1, w_col2, w_col3 = st.columns(3)
w_col1.success("🌡️ **Suhu Air Ideal:**\n\n28°C - 32°C\n\n*(Metabolisme ikan aktif)*")
w_col2.success("🧪 **Nilai pH Kolam:**\n\n6.5 - 8.5\n\n*(Elak ikan stres & penyakit)*")
w_col3.success("🌀 **Oksigen Terlarut (DO):**\n\n> 4.0 mg/L\n\n*(Pasang kincir air waktu malam)*")

st.markdown("---")

# SECTION: KIRAAN BEG LOGISTIK
st.subheader("📦 Kuantiti Anggaran Pembelian & Pecahan Beg Dedak (20kg/Beg)")
b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.info(f"🍼 **Pre-starter**\n\nBerat: {round(feed_pre_starter, 1)} kg\n\n➡️ **{bags_pre} Beg** (RM {bags_pre * price_pre:.2f})")
with b_col2:
    st.success(f"🌱 **Starter**\n\nBerat: {round(feed_starter, 1)} kg\n\n➡️ **{bags_star} Beg** (RM {bags_star * price_star:.2f})")
with b_col3:
    st.warning(f"🥦 **Grower**\n\nBerat: {round(feed_grower, 1)} kg\n\n➡️ **{bags_grow} Beg** (RM {bags_grow * price_grow:.2f})")
with b_col4:
    st.error(f"🍖 **Finisher**\n\nBerat: {round(feed_finisher, 1)} kg\n\n➡️ **{bags_fin} Beg** (RM {bags_fin * price_fin:.2f})")

st.markdown("---")

# LIVE DATA TABLE
st.subheader("📋 Pelan Lengkap Operasi Harian Ladang")
st.dataframe(df, use_container_width=True, hide_index=True)

# EXCEL DOWNLOAD
st.subheader("💾 Eksport Pelan Logistik Ladang")
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df)
st.download_button(
    label="Muat Tunun Pelan Harian Komprehensif (CSV)",
    data=csv_data,
    file_name="Pelan_Operasi_Tilapia_Lengkap.csv",
    mime="text/csv"
)
