import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header & clean layout
st.set_page_config(page_title="Nabils Fish System", layout="wide", page_icon="🐟")

# CSS UI MODEN: SIDEBAR GELAP & SEMUA TEKS PUTIH
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* TETAPAN UMUM TULISAN UTAMA */
    h1, h2, h3, h4, h5, h6, p, span { color: #1C1C1E !important; font-family: 'Inter', sans-serif !important; }
    
    /* SIDEBAR STYLING: KELABU GELAP ELEGAN */
    div[data-testid="stSidebar"] {
        background-color: #1C1C1E !important;
        padding-top: 20px !important;
    }
    
    /* PAKSA SEMUA TEKS, TAJUK, LABEL, & SLIDER DALAM SIDEBAR JADI WARNA PUTIH */
    div[data-testid="stSidebar"] h1, 
    div[data-testid="stSidebar"] h2, 
    div[data-testid="stSidebar"] h3, 
    div[data-testid="stSidebar"] h4, 
    div[data-testid="stSidebar"] label, 
    div[data-testid="stSidebar"] span, 
    div[data-testid="stSidebar"] .stMarkdown p,
    div[data-testid="stSidebar"] .stSlider div {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* KOTAK INPUT ANGKA & SELECTBOX DALAM SIDEBAR */
    div[data-testid="stSidebar"] div[data-testid="stNumberInput"] input,
    div[data-testid="stSidebar"] div[data-testid="stSelectbox"] div {
        background-color: #FFFFFF !important;
        color: #1C1C1E !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 2px solid #00B14F !important;
    }
    
    /* KAD METRIK UTAMA */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 1px solid #E5E5EA !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricValue"] {
        color: #00B14F !important;
        font-weight: 800 !important;
        font-size: 22px !important;
    }
    
    /* KOTAK STATUS AIR & TIPS */
    .status-box-good { padding: 15px; border-radius: 10px; background-color: #E8F5E9; border: 1px solid #C8E6C9; color: #1B5E20 !important; font-weight: 600; margin-bottom: 15px; }
    .status-box-bad { padding: 15px; border-radius: 10px; background-color: #FFEBEE; border: 1px solid #FFCDD2; color: #B71C1C !important; font-weight: 600; margin-bottom: 15px; }
    .tips-card { background-color: #F8F9FA; border-left: 5px solid #00B14F; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; }
    
    /* BUTANG DOWNLOAD */
    .stDownloadButton button {
        background-color: #00B14F !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        width: 100%;
        font-weight: 700 !important;
        padding: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER UTAMA
st.markdown("<h1>🐟 Nabils Fish System: Master Aquaculture Edition</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:15px; font-weight:500; color:#48484A; margin-top:-10px;'>Sistem Lengkap Pengurusan Kolam, Protein Dedak, Kos Belian & Tips Penjagaan Tilapia</p>", unsafe_allow_html=True)
st.markdown("<hr style='border: 0; height: 1px; background: #E5E5EA; margin-bottom: 20px;'/>", unsafe_allow_html=True)

# Pilihan Saiz Benih
size_options = {
    "1.5 Inci": {"weight": 1.2, "price": 0.18},
    "2.0 Inci": {"weight": 2.5, "price": 0.25},
    "2.5 Inci": {"weight": 4.5, "price": 0.35},
    "3.0 Inci": {"weight": 8.0, "price": 0.45},
    "4.0 Inci": {"weight": 22.0, "price": 0.65},
}

# 1. SIDEBAR PARAMETER (SEMUA TEKS PUTIH)
st.sidebar.markdown("### 📋 Parameter Kolam & Benih")
fish_count_input = st.sidebar.number_input("Kuantiti Benih (Ekor)", value=1000, step=100)
selected_size = st.sidebar.selectbox("Saiz Permulaan Benih", list(size_options.keys()), index=1)
initial_weight = size_options[selected_size]["weight"]
seed_price_input = st.sidebar.number_input("Kos Seunit Benih (RM)", value=size_options[selected_size]["price"], step=0.05)

target_weight = st.sidebar.number_input("Sasaran Berat Matang (g)", value=350, step=10)
days_cycle = st.sidebar.number_input("Tempoh Kitaran (Hari)", value=150, step=5)
survival_rate = st.sidebar.slider("Kelangsungan Hidup / SR (%)", min_value=50, max_value=100, value=85, step=5)

st.sidebar.markdown("### 💧 Sensor Kesihatan Air")
water_temp = st.sidebar.slider("Suhu Air Harian (°C)", 22.0, 36.0, 29.0, step=0.5)
dissolved_oxygen = st.sidebar.slider("Oksigen Terlarut (DO mg/L)", 1.0, 10.0, 5.5, step=0.5)

st.sidebar.markdown("### 💵 Harga Kos Dedak (RM/Beg 20kg)")
price_pre = st.sidebar.number_input("Harga Pre-starter", value=90.0, step=5.0)
price_star = st.sidebar.number_input("Harga Starter", value=71.0, step=5.0)
price_grow = st.sidebar.number_input("Harga Grower", value=70.0, step=5.0)
price_fin = st.sidebar.number_input("Harga Finisher", value=70.0, step=5.0)

selling_price_per_kg = st.sidebar.number_input("Harga Jualan (RM/KG)", value=14.0, step=0.5)

# LOGIK AMARAN KUALITI AIR
temp_fcr_multiplier = 1.0
if water_temp < 26.0 or water_temp > 32.0 or dissolved_oxygen < 4.0:
    st.markdown(f"<div class='status-box-bad'>⚠️ AMARAN KRITIKAL AIR!<br/>Suhu: <b>{water_temp}°C</b> | DO: <b>{dissolved_oxygen} mg/L</b>. Kurangkan dedak 15% hari ini bagi elak pembaziran & FCR naik.</div>", unsafe_allow_html=True)
    temp_fcr_multiplier = 1.08
else:
    st.markdown(f"<div class='status-box-good'>🟢 STATUS AIR: Optimum. Tumbesaran ikan dan FCR dalam kawalan.</div>", unsafe_allow_html=True)

# 2. ENGINE PENGIRAAN MODEL
data = []
cumulative_feed = 0
feed_pre = 0; feed_sta = 0; feed_gro = 0; feed_fin = 0
total_mortality_pct = 100 - survival_rate

for d in range(1, int(days_cycle) + 1):
    current_fish_count = fish_count_input - (fish_count_input * (total_mortality_pct / 100) * (d - 1) / (days_cycle - 1))
    w = initial_weight + (target_weight - initial_weight) * (d - 1) / (days_cycle - 1)
    bio = (current_fish_count * w) / 1000
    
    if d <= 14: 
        fr = 7.0; typ = "Pre-starter"; p_price = price_pre; prot = "40% Protein"
    elif d <= 30: 
        fr = 5.0; typ = "Starter"; p_price = price_star; prot = "32% Protein"
    elif d <= 90: 
        fr = 3.0; typ = "Grower"; p_price = price_grow; prot = "28% Protein"
    else: 
        fr = 1.5; typ = "Finisher"; p_price = price_fin; prot = "24% Protein"
        
    feed_day = (bio * fr / 100) * temp_fcr_multiplier
    cumulative_feed += feed_day
    
    if typ == "Pre-starter": feed_pre += feed_day
    elif typ == "Starter": feed_sta += feed_day
    elif typ == "Grower": feed_gro += feed_day
    elif typ == "Finisher": feed_fin += feed_day
    
    berat_awal_kolam = (fish_count_input * initial_weight) / 1000
    kenaikan_bersih = bio - berat_awal_kolam
    fcr_semasa = (cumulative_feed / max(kenaikan_bersih, 0.01))
    
    data.append({
        "Hari": d,
        "Populasi": int(current_fish_count),
        "Purata Berat (g)": round(w, 1),
        "Biomassa (kg)": round(bio, 2),
        "Dedak Harian (kg)": round(feed_day, 2),
        "Fasa Makanan": typ,
        "Protein": prot,
        "FCR Kumulatif": round(fcr_semasa, 2)
    })

df = pd.DataFrame(data)

bags_pre = math.ceil(feed_pre / 20)
bags_sta = math.ceil(feed_sta / 20)
bags_gro = math.ceil(feed_gro / 20)
bags_fin = math.ceil(feed_fin / 20)

total_cost_pre = bags_pre * price_pre
total_cost_sta = bags_sta * price_star
total_cost_gro = bags_gro * price_grow
total_cost_fin = bags_fin * price_fin

total_feed_cost = total_cost_pre + total_cost_sta + total_cost_gro + total_cost_fin
total_seed_cost = fish_count_input * seed_price_input
grand_total_cost = total_feed_cost + total_seed_cost

final_biomass = df["Biomassa (kg)"].iloc[-1]
gross_revenue = final_biomass * selling_price_per_kg
net_profit = gross_revenue - grand_total_cost
final_fcr = df['FCR Kumulatif'].iloc[-1]

st.markdown("<br/>", unsafe_allow_html=True)

# 3. KAD METRIK UTAMA
st.markdown("### 📊 Ringkasan Kewangan & FCR")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Modal Keseluruhan", f"RM {grand_total_cost:,.0f}")
m2.metric("Jualan Kasar", f"RM {gross_revenue:,.0f}")
if net_profit >= 0:
    m3.metric("Untung Bersih", f"RM {net_profit:,.0f}", delta="Positif 👍")
else:
    m3.metric("Defisit / Rugi", f"RM {net_profit:,.0f}", delta="Rugi ⚠️", delta_color="inverse")
m4.metric("Nisbah FCR Akhir", f"{final_fcr}")

st.markdown("<br/>", unsafe_allow_html=True)

# 4. KOTAK LOGISTIK BEG & KOS JUMLAH MENGIKUT FASA
st.markdown("### 📦 Pecahan Kos & Pembelian Beg Dedak (20kg/Beg)")
b1, b2, b3, b4 = st.columns(4)
b1.metric("Pre-starter (40%)", f"{bags_pre} Beg", f"RM {total_cost_pre:,.2f}")
b2.metric("Starter (32%)", f"{bags_sta} Beg", f"RM {total_cost_sta:,.2f}")
b3.metric("Grower (28%)", f"{bags_gro} Beg", f"RM {total_cost_gro:,.2f}")
b4.metric("Finisher (24%)", f"{bags_fin} Beg", f"RM {total_cost_fin:,.2f}")

st.markdown("<hr style='border: 0; height: 1px; background: #E5E5EA; margin: 25px 0;'/>", unsafe_allow_html=True)

# 5. BAHAGIAN TIPS & PANDUAN PENJAGAAN IKAN TILAPIA (PRO SECURE)
st.markdown("### 💡 Panduan & Tips Pro Penjagaan Tilapia untuk FCR Rendah")
t1, t2 = st.columns(2)

with t1:
    st.markdown("""
        <div class='tips-card'>
            <b>1. Teknik Pemberian Makan (Precision Feeding)</b><br/>
            Jangan beri makan sekaligus. Bahagikan kepada 3-4 kali sehari. Hentikan segera jika ikan mula kurang agresif menyambar (tanda kenyang) dalam masa 5 minit bagi mengelak dedak rosak di dasar kolam.
        </div>
        <div class='tips-card'>
            <b>2. Kepentingan Oksigen Terlarut (DO > 5.0 mg/L)</b><br/>
            Oksigen bukan sekadar untuk bernafas, tapi membantu organ usus menghadam protein dengan efisien. Pastikan aerator berfungsi cemerlang terutamanya pada waktu malam dan awal pagi.
        </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
        <div class='tips-card'>
            <b>3. Pengurusan Suhu & Sisa Toksik</b><br/>
            Suhu ideal ialah 28°C - 32°C. Suhu terlalu sejuk melambatkan metabolisme ikan manakala suhu panas merendahkan DO. Lakukan penukaran air berkala jika air bertukar keruh pekat bagi mengawal ammonia.
        </div>
        <div class='tips-card'>
            <b>4. Jadual Grading (Penggredan Saiz)</b><br/>
            Lakukan proses grading setiap 4-5 minggu untuk mengasingkan ikan besar dan kecil. Ini mengelakkan ikan besar membuli ikan kecil daripada mendapat makanan, sekali gus menyeragamkan saiz tuai.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0; height: 1px; background: #E5E5EA; margin: 25px 0;'/>", unsafe_allow_html=True)

# 6. JADUAL OPERASI HARIAN
st.markdown("### 📋 Jadual Logistik Harian & Peratusan Protein")
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("<br/>", unsafe_allow_html=True)
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button("📲 Muat Turun Laporan Penuh Excel (CSV)", data=csv_data, file_name="Nabils_Fish_Master_Report.csv", mime="text/csv")
