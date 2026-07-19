import streamlit as st
import pandas as pd
import numpy as np
import math

# Set up the web page header & mature enterprise layout
st.set_page_config(page_title="Nabils Fish System", layout="wide", page_icon="📈")

# CSS UNTUK BORDER JELAS, KONTRAST TINGGI & ELEGAN
st.markdown("""
    <style>
    /* Global Background & Typography */
    .reportview-container {
        background: #F8FAFC;
    }
    
    /* Nama Sistem & Header Kontras Tinggi */
    h1 {
        color: #0F172A !important;
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h2, h3, h5 {
        color: #1E293B !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
    }
    
    /* Kotak Input Sidebar */
    div[data-testid="stSidebar"] label {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stNumberInput"] input {
        color: #0F172A !important;
        font-weight: 600 !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #1E40AF !important;
        border-radius: 6px;
    }
    
    /* Metric Cards Styling dengan Border Pekat */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 20px 25px;
        border-radius: 8px;
        border: 2px solid #94A3B8;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Custom Info Boxes */
    .pro-box {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #2563EB;
        border-top: 1px solid #CBD5E1;
        border-right: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
        background-color: #EFF6FF;
        color: #1E3A8A;
        font-weight: 500;
    }
    .pro-box-alert {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #DC2626;
        border-top: 1px solid #FCA5A5;
        border-right: 1px solid #FCA5A5;
        border-bottom: 1px solid #FCA5A5;
        background-color: #FEF2F2;
        color: #991B1B;
        font-weight: 500;
    }
    .pro-box-success {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #16A34A;
        border-top: 1px solid #86EFAC;
        border-right: 1px solid #86EFAC;
        border-bottom: 1px solid #86EFAC;
        background-color: #F0FDF4;
        color: #14532D;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER SECTION
st.markdown("<h1>Nabils Fish System</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px; font-weight:600; color:#475569; margin-top:-10px;'><i>Sistem Analisis Akuakultur Kuantitatif & Unjuran Data Perbelanjaan Ladang</i></p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top:5px; margin-bottom:25px; border-color:#94A3B8; border-width: 2px;'/>", unsafe_allow_html=True)

# Data mapping
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

pond_options = {
    "Kolam Simen (Sistem Aliran / Air Bukit)": {
        "fcr_mod": 0.05, 
        "tips": "Fasa operasional kolam simen memerlukan penyingkiran pepejal terampai (najis ikan) secara berkala menerusi sistem central drain atau sifon mingguan.",
        "aerator_rec": "Ring Blower (cth: 370W) dipadankan bersama Aero-Tube/Uniring untuk pemampatan pembebasan micro-bubbles."
    },
    "Kolam Tanah Tradisional": {
        "fcr_mod": -0.10, 
        "tips": "Kehadiran organisma mikro (plankton) mengurangkan kebergantungan penuh pada palet komersial.",
        "aerator_rec": "Sistem Kincir Air (Paddle Wheel) disyorkan bagi mengoptimumkan sirkulasi perimeter air yang luas."
    },
    "Kolam Kanvas / Tangki HDPE": {
        "fcr_mod": 0.00, 
        "tips": "Memudahkan kawalan biosekuriti dan proses penggredan saiz (grading).",
        "aerator_rec": "Aparatus pengudaraan berterusan (Root/Ring Blower) dengan integrasi sistem bekalan kuasa bantuan."
    },
    "Sistem Biofloc": {
        "fcr_mod": -0.20, 
        "tips": "Kitaran penukaran nitrogen memerlukan pengawasan nisbah Karbon:Nitrogen (C:N ratio) yang ketat.",
        "aerator_rec": "Oksigen Terlarut (DO) mestilah dikekalkan secara konsisten pada paras > 5.0 mg/L."
    }
}

# 1. SIDEBAR CONFIGURATION
st.sidebar.markdown("### 📋 Parameter Utama")
fish_count_input = st.sidebar.number_input("Kuantiti Benih (Ekor)", value=1000, step=100)

selected_size = st.sidebar.selectbox("Saiz Permulaan Benih", list(size_options.keys()), index=1)
initial_weight = size_options[selected_size]["weight"]
default_seed_price = size_options[selected_size]["price"]
seed_price_input = st.sidebar.number_input("Kos Seunit Benih (RM)", value=default_seed_price, step=0.05)

selected_pond = st.sidebar.selectbox("Infrastruktur Kolam", list(pond_options.keys()), index=0)
fcr_modifier = pond_options[selected_pond]["fcr_mod"]

target_weight = st.sidebar.number_input("Sasaran Berat Matang (gram)", value=350, step=10)
days_cycle = st.sidebar.number_input("Kitaran Ternakan (Hari)", value=150, step=5)

st.sidebar.markdown("### 🛡️ Pengurusan Risiko")
survival_rate = st.sidebar.slider("Kadar Kelangsungan Hidup / SR (%)", min_value=50, max_value=100, value=85, step=5)

# BOLD & EDITABLE: INPUT KOS & PERATUS PROTEIN DEDAK
st.sidebar.markdown("### 💵 Kos & Kandungan Protein Dedak")

st.sidebar.markdown("**— Pre-starter —**")
price_pre = st.sidebar.number_input("Harga Pre-starter (RM/Beg)", value=90.0, step=5.0)
prot_pre = st.sidebar.number_input("Protein Pre-starter (%)", value=32.0, step=1.0)

st.sidebar.markdown("**— Starter —**")
price_star = st.sidebar.number_input("Harga Starter (RM/Beg)", value=71.0, step=5.0)
prot_star = st.sidebar.number_input("Protein Starter (%)", value=31.0, step=1.0)

st.sidebar.markdown("**— Grower —**")
price_grow = st.sidebar.number_input("Harga Grower (RM/Beg)", value=70.0, step=5.0)
prot_grow = st.sidebar.number_input("Protein Grower (%)", value=29.0, step=1.0)

st.sidebar.markdown("**— Finisher —**")
price_fin = st.sidebar.number_input("Harga Finisher (RM/Beg)", value=70.0, step=5.0)
prot_fin = st.sidebar.number_input("Protein Finisher (%)", value=27.0, step=1.0)

st.sidebar.markdown("### 🏪 Unjuran Nilai Jualan")
selling_price_per_kg = st.sidebar.number_input("Harga Jualan Pasaran (RM/KG)", value=14.0, step=0.5)

# INTERACTIVE ADDITIONAL COSTS
st.markdown("### ⚡ Kos Operasi Tambahan (Penyelenggaraan & Utiliti)")
st.markdown("<p style='font-size:14px; font-weight: 500; color:#475569; margin-top:-10px;'>Masukkan pembolehubah kos luar seperti bil elektrik aerator, rawatan ubat-ubatan, atau kos logistik am.</p>", unsafe_allow_html=True)

if 'additional_costs' not in st.session_state:
    st.session_state.additional_costs = pd.DataFrame([
        {"Komponen Perbelanjaan": "Kos Elektrik Blower HG-370", "Kos Penyelenggaraan (RM)": 150.00},
        {"Komponen Perbelanjaan": "Rawatan Air & Profilaksis (Garam/Kapur)", "Kos Penyelenggaraan (RM)": 50.00}
    ])

edited_costs_df = st.data_editor(
    st.session_state.additional_costs,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Komponen Perbelanjaan": st.column_config.TextColumn("Deskripsi Perbelanjaan"),
        "Kos Penyelenggaraan (RM)": st.column_config.NumberColumn("Kos Penyelenggaraan (RM)", format="RM %.2f", min_value=0.0)
    }
)
st.session_state.additional_costs = edited_costs_df
total_additional_cost = edited_costs_df["Kos Penyelenggaraan (RM)"].sum()

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
        fr = 7.0; typ = "Pre-starter"
        freq = "4 - 5 kali sehari"
        p_price = price_pre
    elif d <= 30: 
        fr = 5.0; typ = "Starter"
        freq = "3 - 4 kali sehari"
        p_price = price_star
    elif d <= 90: 
        fr = 2.8 if d > 60 else 3.8; typ = "Grower"
        freq = "2 - 3 kali sehari"
        p_price = price_grow
    else: 
        fr = 1.5 if d <= 120 else 1.0; typ = "Finisher"
        freq = "2 kali sehari"
        p_price = price_fin
        
    adjusted_fr = max(fr + (fcr_modifier * 2), 0.5)
    feed_day = bio * adjusted_fr / 100
    cumulative_feed += feed_day
    
    if typ == "Pre-starter": feed_pre_starter += feed_day
    elif typ == "Starter": feed_starter += feed_day
    elif typ == "Grower": feed_grower += feed_day
    elif typ == "Finisher": feed_finisher += feed_day
    
    berat_awal_kolam = (fish_count_input * initial_weight) / 1000
    kenaikan_berat_bersih = bio - berat_awal_kolam
    
    fcr_hari_ini = (cumulative_feed / max(kenaikan_berat_bersih, 0.01)) + (fcr_modifier * (d / days_cycle))
    cost_day = feed_day * (p_price / 20)
    sampling_status = "Audit Pensampelan" if d % 30 == 0 or d == 1 else "Rutin Normal"
    
    data.append({
        "Hari": d,
        "Populasi (Ekor)": int(current_fish_count),
        "Purata Berat (g)": round(w, 1),
        "Biomassa (kg)": round(bio, 1),
        "Kadar Dedak (%)": round(adjusted_fr, 2),
        "Dedak Harian (kg)": round(feed_day, 2),
        "Kos Harian (RM)": round(cost_day, 2),
        "Formulasi Dedak": typ,
        "Frekuensi": freq,
        "Tindakan Operasi": sampling_status,
        "Nilai FCR Semasa": round(fcr_hari_ini, 2)
    })

df = pd.DataFrame(data)

bags_pre = math.ceil(feed_pre_starter / 20)
bags_star = math.ceil(feed_starter / 20)
bags_grow = math.ceil(feed_grower / 20)
bags_fin = math.ceil(feed_finisher / 20)

total_feed_cost = (bags_pre * price_pre) + (bags_star * price_star) + (bags_grow * price_grow) + (bags_fin * price_fin)
total_seed_cost = fish_count_input * seed_price_input
grand_total_cost = total_feed_cost + total_seed_cost + total_additional_cost

final_biomass = df["Biomassa (kg)"].iloc[-1]
gross_revenue = final_biomass * selling_price_per_kg
net_profit = gross_revenue - grand_total_cost
final_fcr = df['Nilai FCR Semasa'].iloc[-1]

st.markdown("<br/>", unsafe_allow_html=True)

# 3. EXECUTIVE SUMMARY METRICS
st.markdown("### 📊 Analisis Prestasi Kewangan Kitaran")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Jumlah Komitmen Modal", f"RM {grand_total_cost:.2f}")
with m_col2:
    st.metric("Hasil Jualan Kasar", f"RM {gross_revenue:.2f}")
with m_col3:
    if net_profit >= 0:
        st.metric("Untung Bersih Unjuran", f"RM {net_profit:.2f}", delta="Kedudukan Positif")
    else:
        st.metric("Defisit / Rugi Bersih", f"RM {net_profit:.2f}", delta="Kedudukan Negatif", delta_color="inverse")
with m_col4:
    st.metric("Nisbah Kecekapan FCR", f"{final_fcr}")

# PROFESSIONAL INTERPRETATION BOX
if final_fcr < 1.3:
    st.markdown(f"<div class='pro-box-success'><b>ANALISIS STATUS FCR ({final_fcr}): OPTIMUM TINGGI</b><br/>Kadar penukaran makanan berada pada tahap sangat efisien. Model pengurusan dedak ini memaksimumkan pulangan pelaburan (ROI).</div>", unsafe_allow_html=True)
elif 1.3 <= final_fcr <= 1.5:
    st.markdown(f"<div class='pro-box'><b>ANALISIS STATUS FCR ({final_fcr}): STANDARD OPERASI</b><br/>Prestasi tumbesaran ikan adalah seimbang mengikut piawaian akuakultur komersial serantau.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='pro-box-alert'><b>ANALISIS STATUS FCR ({final_fcr}): PRESTASI KRITIKAL</b><br/>Indikasi kebocoran kos makanan dikesan. Sila nilai semula ketumpatan biomas, pemecahan sistem pengudaraan udara malam, atau kestabilan terma kolam.</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#CBD5E1; border-width: 2px;'/>", unsafe_allow_html=True)

# 4. DATA VISUALIZATION
st.markdown("### 📈 Visualisasi Data Projeksi (Boleh di-zoom & Hover)")
g_col1, g_col2 = st.columns(2)

with g_col1:
    st.markdown("<div style='border: 2px solid #CBD5E1; padding: 15px; border-radius: 8px; background-color: #FFFFFF;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:15px; font-weight:700; color:#0F172A; margin-top:0px;'>Korelasi Purata Berat Per Ekor (g) vs Keperluan Dedak Harian (kg)</p>", unsafe_allow_html=True)
    chart_data1 = df.set_index("Hari")[["Purata Berat (g)", "Dedak Harian (kg)"]]
    st.area_chart(chart_data1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with g_col2:
    st.markdown("<div style='border: 2px solid #CBD5E1; padding: 15px; border-radius: 8px; background-color: #FFFFFF;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:15px; font-weight:700; color:#0F172A; margin-top:0px;'>Trend Akumulasi Biomassa (kg) menentang Unjuran FCR Semasa</p>", unsafe_allow_html=True)
    chart_data2 = df.set_index("Hari")[["Biomassa (kg)", "Nilai FCR Semasa"]]
    st.line_chart(chart_data2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/><hr style='border-color:#CBD5E1; border-width: 2px;'/>", unsafe_allow_html=True)

# 5. DYNAMIC LOGISTICS & PROTEIN % MATCHING
st.markdown("### 📦 Spesifikasi Logistik Pembelian Makanan & Kelebihan Nutrisi")
st.markdown("<p style='font-size:14px; font-weight: 500; color:#475569; margin-top:-10px;'>Pecahan jumlah beg (20kg/beg) beserta data peratus protein makro untuk kawalan FCR yang optimum.</p>", unsafe_allow_html=True)

b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    st.metric(f"Pre-starter ({prot_pre:.1f}% Protein)", f"{bags_pre} Beg", f"Kos: RM {bags_pre * price_pre:.2f}", delta_color="off")
    st.markdown("<p style='font-size:13px; color:#1E293B; font-weight:500; line-height:1.4;'><b>Kelebihan FCR:</b> Kadar asimilasi tinggi untuk benih kecil. Protein tinggi memecah sekatan tumbesaran awal (stunting) dan membina imuniti organ dalaman.</p>", unsafe_allow_html=True)

with b_col2:
    st.metric(f"Starter ({prot_star:.1f}% Protein)", f"{bags_star} Beg", f"Kos: RM {bags_star * price_star:.2f}", delta_color="off")
    st.markdown("<p style='font-size:13px; color:#1E293B; font-weight:500; line-height:1.4;'><b>Kelebihan FCR:</b> Nisbah asid amino seimbang untuk fasa pembentukan struktur tulang rangka utama ikan. Memastikan pertambahan panjang badan yang seragam.</p>", unsafe_allow_html=True)

with b_col3:
    st.metric(f"Grower ({prot_grow:.1f}% Protein)", f"{bags_grow} Beg", f"Kos: RM {bags_grow * price_grow:.2f}", delta_color="off")
    st.markdown("<p style='font-size:13px; color:#1E293B; font-weight:500; line-height:1.4;'><b>Kelebihan FCR:</b> Mengoptimumkan pembentukan tisu otot daging tebal. Tahap protein dilaraskan supaya ikan tidak membuang sisa nitrogen berlebihan ke dalam air kolam.</p>", unsafe_allow_html=True)

with b_col4:
    st.metric(f"Finisher ({prot_fin:.1f}% Protein)", f"{bags_fin} Beg", f"Kos: RM {bags_fin * price_fin:.2f}", delta_color="off")
    st.markdown("<p style='font-size:13px; color:#1E293B; font-weight:500; line-height:1.4;'><b>Kelebihan FCR:</b> Mengekalkan berat badan sasaran komersial tanpa pengumpulan lemak (fatty liver). Membantu mengekalkan tekstur daging yang pejal sebelum tuaian.</p>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#CBD5E1; border-width: 2px;'/>", unsafe_allow_html=True)

# 6. HUB ILMU & PETUA TEKNIKAL
st.markdown("### 📚 Pangkalan Pengetahuan & Pengurusan Risiko")
with st.expander("🔬 Analisis Parameter Saintifik & Biologi"):
    st.markdown("""
    * **Metabolisme Terma:** Kitaran biologi Tilapia Merah beroperasi secara optimum pada julat suhu **28°C - 32°C**. Penukuran suhu bawah julat ini merencat enzim pencernaan.
    * **Mekanisme Larutan Oksigen:** Pemasangan sistem pemampatan *micro-bubbles* meningkatkan kadar *Dissolved Oxygen* (DO) jauh lebih efektif berbanding buih kasar.
    """)

with st.expander("💡 Garis Panduan Praktikal & Operasi Lapangan"):
    st.markdown("""
    * **Kitaran Hidraulik Air Bukit:** Elakkan kemasukan air bukit berterusan jika ia menjejaskan suhu terma air kolam simen.
    * **Metodologi Pemakanan Satiation:** Pemberian palet harus dihentikan serta-merta apabila tindak balas suapan ikan menurun melebihi 5 minit.
    """)

with st.expander(f"⚙️ Spesifikasi Teknikal Infrastruktur: {selected_pond}"):
    p_col1, p_col2 = st.columns(2)
    p_col1.info(f"**Pengurusan Sisa:**\n\n{pond_options[selected_pond]['tips']}")
    p_col2.warning(f"**Konfigurasi Pengudaraan:**\n\n{pond_options[selected_pond]['aerator_rec']}")

st.markdown("<hr style='border-color:#CBD5E1; border-width: 2px;'/>", unsafe_allow_html=True)

# 7. JADUAL MATRIKS OPERASI
st.markdown("### 📋 Jadual Matriks Operasi Harian (Boleh Cari & Susun)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("<br/>", unsafe_allow_html=True)
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Muat Turun Pelan Data CSV (Eksport Logistik)",
    data=csv_data,
    file_name="Pelan_Operasi_Tilapia_Lengkap.csv",
    mime="text/csv"
)
