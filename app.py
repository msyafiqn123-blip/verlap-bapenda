import streamlit as st
from st_keyup import st_keyup
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
try:
    from supabase import create_client, Client
except ImportError:
    pass
import os
import datetime
from math import radians, cos, sin, asin, sqrt, degrees, atan2
from streamlit_geolocation import streamlit_geolocation
import json
import random

try:
    from shapely.geometry import shape, mapping, Polygon, Point
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

# --- CONFIGURATION ---
from PIL import Image
try:
    import os
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bapenda.png")
    page_icon = Image.open(logo_path)
except:
    page_icon = "🏛️"

# 2. KONFIGURASI HALAMAN STREAMLIT
st.set_page_config(
    page_title="Sistem Verifikasi Lapangan",
    page_icon="bapenda.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sembunyikan menu Streamlit dan tombol Deploy
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none !important;}
[data-testid="stAppCreatorBadge"], [data-testid="viewerBadge"], [data-testid="manage-app-badge"], a[href*="streamlit"], a[href*="msyafiqn123"], a[href*="github"] {display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;}
[data-testid="stAppViewBlockContainer"] {padding-top: 2rem;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def format_nop_string(val):
    if not val:
        return ""
    v = str(val).replace(".", "").replace("-", "").strip()
    if len(v) == 18:
        return f"{v[0:2]}.{v[2:4]}.{v[4:7]}.{v[7:10]}.{v[10:13]}.{v[13:17]}.{v[17:]}"
    return val

BAPENDA_COORD = [-6.5459027, 107.445524]


# --- CUSTOM CSS FOR MODERN UI (VERCEL/REACT STYLE) ---
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #f8fafc !important; /* Slate 50 - clean off-white */
        color: #1e293b !important; /* Slate 800 */
    }
    
    /* Hide Streamlit Default Headers/Footers & Creator Badges for Immersive App Feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stAppCreatorBadge"],
    [data-testid="viewerBadge"],
    [data-testid="manage-app-badge"],
    a[href*="streamlit"],
    a[href*="msyafiqn123"],
    a[href*="github.com"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Prevent horizontal scroll */
    .stApp, html, body {
        overflow-x: hidden !important;
    }
    
    /* Remove large whitespace at the top */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Title and Headers Styling */
    h1, h2, h3, h4 {
        color: #0f172a !important; /* Slate 900 */
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    
    /* Modern Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e2e8f0; /* Slate 200 */
        padding: 6px;
        border-radius: 12px;
        box-shadow: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        color: #64748b; /* Slate 500 */
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #f97316 !important; /* Bapenda Orange */
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) !important;
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgb(249 115 22 / 0.2), 0 2px 4px -2px rgb(249 115 22 / 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgb(249 115 22 / 0.3), 0 4px 6px -2px rgb(249 115 22 / 0.3);
        border: none;
    }
    
    /* Form Inputs & Selectboxes */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        border-radius: 8px;
        border: 1px solid #cbd5e1; /* Slate 300 */
        background-color: white;
        transition: all 0.2s;
    }
    div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover {
        border-color: #94a3b8;
    }
    
    /* Dataframes / Tables as Cards */
    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        border: 1px solid #f1f5f9;
    }
    
    /* Alert / Success Banners */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
    
    /* Mobile Responsiveness / Optimization */
    @media (max-width: 768px) {
        /* Make Tabs wrap instead of scroll on mobile */
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            flex-wrap: wrap !important;
            flex-direction: row !important;
            overflow-x: hidden !important;
            gap: 6px;
            padding: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            flex-grow: 1 !important;
            justify-content: center !important;
            width: auto !important;
            padding: 10px 14px;
            font-size: 0.95rem; /* Medium touch target */
            white-space: normal !important;
        }
        /* Reduce overall page margins to maximize screen estate */
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        /* Resize huge titles */
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.2 !important;
        }
    }
</style>
''', unsafe_allow_html=True)

# --- SUPABASE CONNECTION ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
USE_MOCK_DATA = False

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = None
if SUPABASE_URL != "YOUR_SUPABASE_URL":
    supabase = init_connection()

if not supabase:
    st.info("ℹ️ Menjalankan aplikasi dengan DATA DUMMY (Mock Mode) karena koneksi Supabase belum disetel.")
    USE_MOCK_DATA = True

import math

# --- HELPER FUNCTIONS ---
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 
    return c * r

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    brng = math.atan2(y, x)
    brng = (math.degrees(brng) + 360) % 360
    return brng

def get_compass_direction(bearing):
    if 315 <= bearing or bearing < 45: return "Utara"
    if 45 <= bearing < 135: return "Timur"
    if 135 <= bearing < 225: return "Selatan"
    if 225 <= bearing < 315: return "Barat"
    return "Lainnya"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner="🗺️ Memuat data wilayah...")
def load_referensi():
    # cache bust v2
    filepath = os.path.join(BASE_DIR, "referensi_wilayah.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data(show_spinner="🗺️ Memuat peta batas desa...")
def load_geojson(filename):
    # cache bust v2
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data(show_spinner="🔍 Memuat kamus NOP...")
def load_referensi_nop():
    # cache bust v2
    filepath = os.path.join(BASE_DIR, "referensi_nop.json")
    if os.path.exists(filepath):
        import json
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def init_mock_data():
    if 'mock_berkas' not in st.session_state:
        import uuid
        import datetime
        import random
        data = []
        kategori = ['Berkas Pendataan', 'Berkas Objek Baru', 'Berkas BPHTB']
        statuses = [
            'Belum', 'Belum', 'Belum', 'Belum', 'Belum',
            'Belum', 'Belum', 'Belum', 'Belum', 'Belum',
            'Belum', 'Belum', 'Belum', 'Belum', 'Belum',
            'Dijadwalkan', 'Sudah', 'Dijadwalkan', 'Belum', 'Belum'
        ]
        ref_nop = load_referensi_nop()
        kode_list = list(ref_nop.keys()) if ref_nop else []
        
        for i in range(20):
            kat = random.choice(kategori)
            is_bphtb = (kat == 'Berkas BPHTB')
            if is_bphtb:
                nopel = f'0126{1478+i}'
            else:
                nopel = f'2026.{(i+1):04d}.001'
                
            nm_kec = "PURWAKARTA"
            nm_kel = "NAGRI TENGAH"
            nop_kode = f'32.16.011.001.000.{i:04d}.0'
            
            if kode_list:
                rand_kode = random.choice(kode_list)
                nm_kec = ref_nop[rand_kode]['kecamatan']
                nm_kel = ref_nop[rand_kode]['kelurahan']
                # re-construct a dummy NOP with the valid code
                nop_kode = f'32.16.{rand_kode[:3]}.{rand_kode[3:]}.000.{i:04d}.0'
                
            data.append({
                'id': str(uuid.uuid4()),
                'nomor_pelayanan': nopel,
                'nomor_nop': nop_kode,
                'nama_pemohon': f'Pemohon {chr(64+i+1)}',
                'tanggal_input': (datetime.date.today() - datetime.timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d'),
                'is_urgent': random.choice([True, False, False]),
                'keterangan_berkas': kat,
                'kecamatan': nm_kec,
                'desa': nm_kel,
                'status_survey': statuses[i],
                'lat': BAPENDA_COORD[0] + random.uniform(-0.05, 0.05),
                'lon': BAPENDA_COORD[1] + random.uniform(-0.05, 0.05)
            })
        st.session_state.mock_berkas = data


def generate_surat_perintah(berkas_list, pegawai_list, tanggal_survei, nomor_surat="340"):
    from fpdf import FPDF
    import datetime
    
    class PDF(FPDF):
        def footer(self):
            self.set_y(272)
            self.set_font("calibri", "", 10)
            self.line(15, 275, 195, 275)
            # Add BSrE logo if exists
            import os
            if os.path.exists('logo_bsre.png'):
                try:
                    self.image('logo_bsre.png', 15, 277, 25)
                except:
                    pass
            
            self.set_y(278)
            self.set_x(15)
            self.cell(180, 4, "Dokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik yang diterbitkan oleh", ln=True, align="R")
            self.set_x(15)
            self.cell(180, 4, "Balai Sertifikat Elektronik (BSrE) Badan Siber dan Sandi Negara", ln=True, align="R")

    pdf = PDF(format='legal')
    pdf.add_font("calibri", "", "calibri.ttf", uni=True)
    pdf.add_font("calibri", "B", "calibrib.ttf", uni=True)
    pdf.add_page()
    
    import os
    logo_path = "logo_pwk.png"
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, 15, 8, w=21)
        except:
            pass
    
    # Header
    pdf.set_font("calibri", "B", 16)
    pdf.cell(0, 6, "PEMERINTAH KABUPATEN PURWAKARTA", ln=True, align="C")
    pdf.set_font("calibri", "B", 22)
    pdf.cell(0, 8, "BADAN PENDAPATAN DAERAH", ln=True, align="C")
    pdf.set_font("calibri", "", 12)
    pdf.cell(0, 5, "Jalan Surawinata No. 30. A Purwakarta Kode Pos 41114", ln=True, align="C")
    pdf.cell(0, 4, "e-mail: bapenda@purwakartakab.go.id", ln=True, align="C")
    
    # Line
    pdf.set_y(38)
    pdf.line(15, 38, 195, 38)
    pdf.ln(8)
    
    # Title
    pdf.set_font("calibri", "BU", 16)
    pdf.set_font("calibri", "BU", 18)
    pdf.cell(0, 6, "SURAT PERINTAH", ln=True, align="C")
    pdf.set_font("calibri", "", 14)
    pdf.cell(0, 5, f"Nomor: 800.1.11.1/{nomor_surat}/PENDANIL/2026", ln=True, align="C")
    pdf.ln(10)
    
    # Dari / Issuer
    pdf.set_font("calibri", "", 12)
    pdf.cell(15, 5, "", 0, 0)
    pdf.cell(20, 5, "Nama", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    pdf.cell(0, 5, "EDI PURWANA, S.Si, M.Akt", ln=True)
    
    pdf.cell(15, 5, "", 0, 0)
    pdf.cell(20, 5, "NIP", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    pdf.cell(0, 5, "19800523 201001 1 004", ln=True)
    
    pdf.cell(15, 5, "", 0, 0)
    pdf.cell(20, 5, "Jabatan", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    pdf.cell(0, 5, "Kepala Bidang Pendataan dan Penilaian", ln=True)
    pdf.cell(40, 5, "", 0, 0)
    pdf.cell(0, 5, "Badan Pendapatan Daerah Kabupaten Purwakarta", ln=True)
    pdf.ln(10)
    
    # Memerintahkan
    pdf.set_font("calibri", "B", 14)
    pdf.cell(0, 5, "MEMERINTAHKAN", ln=True, align="C")
    pdf.ln(5)
    
    # Kepada
    pdf.set_font("calibri", "", 12)
    pdf.cell(15, 5, "", 0, 0)
    pdf.cell(20, 5, "Kepada", 0, 0)
    pdf.cell(5, 5, ":", 0, 1)
    
    for i, p in enumerate(pegawai_list):
        if i == 0:
            pdf.cell(15, 5, "", 0, 0)
            pdf.cell(20, 5, "Nama", 0, 0)
            pdf.cell(5, 5, ":", 0, 0)
        else:
            pdf.cell(40, 5, "", 0, 0)
            
        pdf.cell(5, 5, f"{i+1}.", 0, 0)
        pdf.cell(22, 5, "NAMA", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, p['nama_pegawai'].upper().split(" (")[0], ln=True)
        
        pdf.cell(45, 5, "", 0, 0)
        pdf.cell(22, 5, "NIP", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, p['nip'], ln=True)
        
        pdf.cell(45, 5, "", 0, 0)
        pdf.cell(22, 5, "JABATAN", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, p.get('jabatan', "PENGOLAH DATA DAN INFORMASI"), ln=True)
        pdf.ln(3)
        
    pdf.ln(2)
    
    # Untuk
    pdf.cell(15, 5, "", 0, 0)
    pdf.cell(20, 5, "Untuk", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    
    x = pdf.get_x()
    y = pdf.get_y()
    
    teks_untuk = "Melakukan Verifikasi Lapangan sehubungan dengan permohonan pelayanan Pajak Bumi dan Bangunan sesuai dengan permohonan atas:"
    if berkas_list:
        kategori = str(berkas_list[0].get('keterangan_berkas', '')).upper()
        if 'BPHTB' in kategori:
            teks_untuk = "Melakukan Verifikasi Lapangan sehubungan dengan permohonan Formulir Penelitian SSPD-BPHTB yang diragukan sesuai dengan permohonan atas:"
            
    pdf.multi_cell(0, 5, teks_untuk)
    pdf.ln(2)
    
    for b in berkas_list:
        pdf.set_x(x)
        pdf.cell(30, 5, "Nama", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, b['nama_pemohon'].upper(), ln=True)
        
        pdf.set_x(x)
        pdf.cell(30, 5, "No.Pendaftaran", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, b['nomor_pelayanan'], ln=True)
        
        pdf.set_x(x)
        pdf.cell(30, 5, "NOP", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, format_nop_string(b['nomor_nop']), ln=True)
        
        pdf.set_x(x)
        pdf.cell(30, 5, "Letak Tanah", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, f"KP WARNASARI", ln=True)
        
        pdf.set_x(x)
        pdf.cell(30, 5, "Desa", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, b['desa'].upper(), ln=True)
        
        pdf.set_x(x)
        pdf.cell(30, 5, "Kecamatan", 0, 0)
        pdf.cell(5, 5, ":", 0, 0)
        pdf.cell(0, 5, b['kecamatan'].upper(), ln=True)
        pdf.ln(5)
        
    pdf.set_x(x)
    hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][tanggal_survei.weekday()]
    bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"][tanggal_survei.month - 1]
    pdf.multi_cell(0, 5, f"dilaksanakan pada hari {hari} , {tanggal_survei.day} {bulan} {tanggal_survei.year}")
    
    pdf.set_x(x)
    pdf.multi_cell(0, 5, "Demikian surat perintah ini dikeluarkan untuk dilaksanakan dan melaporkan hasilnya.")
    pdf.ln(10)
    
    # Signatures
    pdf.set_x(120)
    pdf.cell(30, 5, "Dikeluarkan di", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    pdf.cell(0, 5, "Purwakarta", ln=True)
    
    pdf.set_x(120)
    pdf.cell(30, 5, "Pada tanggal", 0, 0)
    pdf.cell(5, 5, ":", 0, 0)
    today = datetime.date.today()
    pdf.cell(0, 5, f"{today.day} {bulan} {today.year}", ln=True)
    pdf.ln(5)
    
    pdf.set_x(120)
    pdf.multi_cell(0, 5, "A.n Kepala Badan Pendapatan Daerah\nKabupaten Purwakarta\nKepala Bidang Pendataan dan Penilaian")
    
    return bytes(pdf.output(dest='S'))


@st.cache_data(ttl=15)
def fetch_berkas(kecamatan=None, status=None, only_urgent=False):
    global USE_MOCK_DATA
    df = pd.DataFrame()
    if not USE_MOCK_DATA:
        try:
            query = supabase.table('berkas').select('*')
            if kecamatan and kecamatan != "Semua":
                query = query.eq('kecamatan', kecamatan)
            if status and status != "Semua":
                query = query.eq('status_survey', status)
            if only_urgent:
                query = query.eq('mendesak', True)
            response = query.execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                rename_map = {
                    'latitude': 'lat',
                    'longitude': 'lon',
                    'no_pelayanan': 'nomor_pelayanan',
                    'kategori_berkas': 'keterangan_berkas',
                    'kelurahan': 'desa',
                    'mendesak': 'is_urgent'
                }
                if 'created_at' in df.columns:
                    rename_map['created_at'] = 'tanggal_input'
                
                df = df.rename(columns=rename_map)
                
                import datetime
                if 'tanggal_input' not in df.columns:
                    df['tanggal_input'] = datetime.date.today().strftime('%Y-%m-%d')
                else:
                    df['tanggal_input'] = pd.to_datetime(df['tanggal_input']).dt.strftime('%Y-%m-%d')
        except Exception as e:
            st.error(f"Gagal mengambil data dari Supabase: {e}")
            
    if USE_MOCK_DATA:
        init_mock_data()
        df = pd.DataFrame(st.session_state.mock_berkas)
        if not df.empty:
            df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        
    if not df.empty and kecamatan and kecamatan != "Semua":
        df = df[df['kecamatan'] == kecamatan]
    if not df.empty and status and status != "Semua":
        df = df[df['status_survey'] == status]
    if not df.empty and only_urgent:
        df = df[df['is_urgent'] == True]
        
    if df.empty:
        df = pd.DataFrame(columns=[
            'id', 'nomor_pelayanan', 'nomor_nop', 'nama_pemohon', 'tanggal_input', 
            'mendesak', 'is_urgent', 'kategori_berkas', 'keterangan_berkas', 
            'kecamatan', 'kelurahan', 'desa', 'status_survey', 'lat', 'lon'
        ])
    return df

@st.cache_data(ttl=60)
def fetch_pegawai():
    try:
        response = supabase.table('tabel_pegawai').select('*').execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            raise Exception("Tabel kosong")
            
        # Patch jabatan Syafiq jika dari database masih salah
        df.loc[df['nama_pegawai'] == "MUHAMMAD SYAFIQ N", 'jabatan'] = "PENGOLAH DATA DAN INFORMASI"
            
        return df
    except Exception as e:
        # Fallback to hardcoded list if table doesn't exist or permission denied
        names = [
            "PEVI AZIASTUTI.SE, M.Tr.A.P",
            "YUDHANTARA",
            "SEPTI KHOERUNNISA",
            "DEDEN JUNAEDI",
            "IWAN GUNAWAN",
            "MUHAMAD TAUFIK",
            "AGHISNA DIANITASHA P",
            "MUHAMMAD SYAFIQ N",
            "TRIA RIZKIA IRAWAN",
            "ATA",
            "DADAN ISKANDAR, SE"
        ]
        nips = [
            "19741205 200801 2 009",
            "19780619 200701 1 008",
            "199309102025212093",
            "19811204 200801 1 002",
            "19811201 200901 1 003",
            "20020120 202302 1 001",
            "199508212022032014",
            "19931215 202421 1 006",
            "19920119 202421 1 001",
            "19850617 200901 1 001",
            "19740510 200801 1 007"
        ]
        jabatans = [
            "KASUBID PENDATAAN, PENILAIAN PBB P2 DAN BPHTB",
            "PENGOLAH DATA DAN INFORMASI PENILAIAN",
            "PENATA LAYANAN OPERASIONAL",
            "PENGELOLA PAJAK DAERAH",
            "PENGELOLA PAJAK DAERAH",
            "PENGOLAH DATA DAN INFORMASI",
            "PENATA LAYANAN OPERASIONAL",
            "PENGOLAH DATA DAN INFORMASI",
            "PENATA LAYANAN OPERASIONAL",
            "PENELAAH TEKNIS KEBIJAKAN",
            "PENGELOLA PAJAK DAERAH"
        ]
        data = {
            'id': [f'peg-{i+1}' for i in range(len(names))],
            'nama_pegawai': names,
            'nip': nips,
            'jabatan': jabatans
        }
        return pd.DataFrame(data)

def optimize_multiple_routes(df):
    """
    Groups points by compass direction relative to Bapenda,
    then runs a Greedy TSP within each direction to ensure no bolak-balik.
    """
    if df.empty or 'lat' not in df.columns or df['lat'].isnull().all():
        return {}
    
    df_clean = df.dropna(subset=['lat', 'lon']).copy()
    
    for idx, row in df_clean.iterrows():
        brng = calculate_bearing(BAPENDA_COORD[0], BAPENDA_COORD[1], row['lat'], row['lon'])
        df_clean.at[idx, 'arah'] = get_compass_direction(brng)
        
    routes_dict = {}
    
    for arah, group in df_clean.groupby('arah'):
        unvisited = group.to_dict('records')
        current_loc = {'lat': BAPENDA_COORD[0], 'lon': BAPENDA_COORD[1]}
        route = []
        
        while unvisited:
            nearest_idx = 0
            min_dist = float('inf')
            for i, point in enumerate(unvisited):
                dist = haversine(current_loc['lon'], current_loc['lat'], point['lon'], point['lat'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i
                    
            next_point = unvisited.pop(nearest_idx)
            route.append(next_point)
            current_loc = {'lat': next_point['lat'], 'lon': next_point['lon']}
            
        routes_dict[arah] = route
        
    return routes_dict

def get_feature_by_name(geojson_data, name_value, key='name'):
    if not geojson_data:
        return None
    for feature in geojson_data.get('features', []):
        if str(feature['properties'].get(key, '')).upper() == str(name_value).upper():
            return feature
    return None

def create_dynamic_mask(geom_to_highlight):
    """Membuat GeoJSON mask dunia dikurangi geom_to_highlight"""
    if not HAS_SHAPELY or not geom_to_highlight:
        return None
    try:
        world_poly = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90), (-180, -90)])
        mask_geom = world_poly.difference(geom_to_highlight)
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"name": "Mask"},
                "geometry": mapping(mask_geom)
            }]
        }
    except Exception:
        return None

# --- UI COMPONENTS ---
bapenda_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bapenda.png")
import os, base64
if os.path.exists(bapenda_logo_path):
    with open(bapenda_logo_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'''
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="data:image/png;base64,{img_b64}" width="55" />
            <h1 style="margin: 0; padding: 0;">Sistem Verifikasi Lapangan</h1>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.title("Sistem Verifikasi Lapangan")
st.markdown("**Subbid PBB & BPHTB, Bidang Pendataan dan Penilaian - Bapenda Kabupaten Purwakarta**")

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Input Berkas Baru", "📍 Peta Interaktif & Filter", "👥 Penugasan (Admin)", "📊 Dashboard Workload", "📱 Update Lapangan (Petugas)", "🔍 Cek Status Berkas"])

import streamlit.components.v1 as components
if 'mobile_tab_switched' not in st.session_state:
    st.session_state.mobile_tab_switched = True
    components.html("""
    <script>
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
        setTimeout(() => {
            const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
            if (tabs.length >= 5) {
                tabs[4].click();
            }
        }, 500);
    }
    </script>
    """, height=0, width=0)


# --- TAB 0: INPUT BERKAS BARU ---
with tab0:
    st.header("📝 Input Antrean Berkas Baru")
    st.write("Tambahkan data berkas yang akan disurvei lapangan. Berkas akan masuk ke Daftar Tunggu (Belum Disurvei).")
    
    @st.cache_data(ttl=300, show_spinner="🔃 Proses sinkronisasi data...")
    def fetch_spreadsheet_data():
        import pandas as pd
        url = "https://docs.google.com/spreadsheets/d/1mrbqAXbRDK7MR-rjlMsVxFzzo6jlhxHpbtHAT5W55RQ/export?format=xlsx"
        try:
            dfs = pd.read_excel(url, sheet_name=None, header=None, skiprows=3)
            return pd.concat(dfs.values(), ignore_index=True)
        except:
            return pd.DataFrame()

    df_sheet = fetch_spreadsheet_data()
    
    col_nopel, col_btn = st.columns([4, 1])
    with col_nopel:
        nopel_baru = st.text_input("Nomor Pelayanan", placeholder="Contoh: 2026.0001.134", help="Ketik Nomor Pelayanan, data akan disinkronisasikan secara otomatis jika cocok.")
    with col_btn:
        st.write("")
        st.write("")
        cek_btn = st.button("🔍 Cek", use_container_width=True)
    
    matched_row = None
    if nopel_baru and not df_sheet.empty:
        import pandas as pd
        df_sheet[2] = df_sheet[2].astype(str).str.strip()
        match = df_sheet[df_sheet[2] == nopel_baru.strip()]
        if not match.empty:
            matched_row = match.iloc[0]
            st.success("✅ Data Nomor Pelayanan ditemukan (Sinkronisasi sukses)")
        elif nopel_baru.strip().startswith("0"):
            st.info("ℹ️ Berkas BPHTB terdeteksi. Silakan input NOP & Nama Pemohon secara manual (Kecamatan/Kelurahan otomatis dari NOP).")
        elif cek_btn:
            st.error("❌ Data Nomor Pelayanan tidak ditemukan")
            
    import pandas as pd
    default_nop = str(matched_row[3]).strip() if matched_row is not None and not pd.isna(matched_row[3]) else "32.16."
    default_nama = str(matched_row[4]).strip() if matched_row is not None and not pd.isna(matched_row[4]) else ""
    jenis_permohonan = str(matched_row[5]).strip().upper() if matched_row is not None and not pd.isna(matched_row[5]) else ""
    
    cat_index = 0
    if nopel_baru and nopel_baru.strip().startswith("0"):
        cat_index = 1
    elif "OBJEK BARU" in jenis_permohonan:
        cat_index = 2
    elif "BPHTB" in jenis_permohonan:
        cat_index = 1
    
    kategori_baru = st.selectbox("Kategori Berkas", ["Berkas Pendataan", "Berkas BPHTB", "Berkas Objek Baru"], index=cat_index)
    
    col1, col2 = st.columns(2)
    with col1:
        nop_baru = st.text_input("Nomor NOP", value=default_nop, placeholder="Contoh: 32.16.031...")
        
        import streamlit.components.v1 as components
        import re
        components.html(
            """
            <script>
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('input[aria-label="Nomor NOP"]');
            
            if (inputs.length > 0) {
                let input = inputs[0];
                input.addEventListener('input', function(e) {
                    let val = e.target.value.replace(/\\D/g, '');
                    
                    if (val.length < 4) {
                        val = '3216';
                    } else if (val.substring(0, 4) !== '3216') {
                        val = '3216' + val.substring(4);
                    }
                    
                    let res = '32.16.';
                    if(val.length > 4) res += val.substring(4, 7);
                    if(val.length > 7) res += '.' + val.substring(7, 10);
                    if(val.length > 10) res += '.' + val.substring(10, 13);
                    if(val.length > 13) res += '.' + val.substring(13, 17);
                    if(val.length > 17) res += '.' + val.substring(17, 18);
                    
                    if (e.target.value !== res) {
                        e.target.value = res;
                        let tracker = e.target._valueTracker;
                        if (tracker) {
                            tracker.setValue(res);
                        }
                        e.target.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
            
            const inputsPel = doc.querySelectorAll('input[aria-label="Nomor Pelayanan"]');
            if (inputsPel.length > 0) {
                let inpPel = inputsPel[0];
                inpPel.addEventListener('input', function(e) {
                    let val = e.target.value;
                    if (val.startsWith("2")) {
                        let digits = val.replace(/\D/g, '');
                        let res = '';
                        if (digits.length > 0) res = digits.substring(0, 4);
                        if (digits.length > 4) res += '.' + digits.substring(4, 8);
                        if (digits.length > 8) res += '.' + digits.substring(8, 11);
                        
                        if (e.target.value !== res) {
                            e.target.value = res;
                            let tracker = e.target._valueTracker;
                            if (tracker) tracker.setValue(res);
                            e.target.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                });
            }
            </script>
            """,
            height=0,
            width=0,
        )
        
        nop_clean_preview = re.sub(r'\D', '', nop_baru if nop_baru else "")
        
        # 2. Tampilkan Lokasi

        if len(nop_clean_preview) >= 10:
            kode_prev = nop_clean_preview[4:10]
            ref_nop = load_referensi_nop()
            if kode_prev in ref_nop:
                st.success(f"📍 {ref_nop[kode_prev]['kecamatan']} - {ref_nop[kode_prev]['kelurahan']}")
            elif len(nop_clean_preview) >= 18:
                st.warning("⚠️ Kode Kecamatan/Kelurahan pada NOP tidak valid (Bukan wilayah Purwakarta)")
    with col2:
        pemohon_baru = st.text_input("Nama Pemohon", value=default_nama, placeholder="Nama Wajib Pajak")
        urgensi_baru = st.checkbox("🔥 Tandai sebagai MENDESAK (Prioritas Utama)")
        
    st.info("💡 Kecamatan dan Kelurahan akan terisi otomatis berdasarkan 18 digit Nomor NOP. Pastikan NOP terisi dan valid (Misal: 32.16.080.014...).")
    st.markdown("**Titik Koordinat Geografis** (Opsional)")
    
    if 'cached_gmaps_link' not in st.session_state:
        st.session_state.cached_gmaps_link = ""
        st.session_state.cached_gmaps_lat = ""
        st.session_state.cached_gmaps_lon = ""
        st.session_state.gmaps_status_msg = None
        
    gmaps_col1, gmaps_col2 = st.columns([4, 1])
    with gmaps_col1:
        gmaps_link = st.text_input("Atau Paste Link Google Maps", placeholder="https://maps.app.goo.gl/...", label_visibility="collapsed")
    with gmaps_col2:
        cek_btn = st.button("🔍 Cek", use_container_width=True, key="btn_cek_gmaps")
    
    if cek_btn and gmaps_link:
        import requests
        import re
        import urllib.parse
        st.session_state.cached_gmaps_link = gmaps_link
        st.session_state.gmaps_status_msg = None
        try:
            with st.spinner("Mengekstrak..."):
                resp = requests.get(gmaps_link, allow_redirects=True, timeout=5)
                f_url = urllib.parse.unquote(resp.url)
                m1 = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', f_url)
                m2 = re.search(r'search/(-?\d+\.\d+),\s*\+?(-?\d+\.\d+)', f_url)
                m3 = re.search(r'q=(-?\d+\.\d+),\s*(-?\d+\.\d+)', f_url)
                m4 = re.search(r'll=(-?\d+\.\d+),\s*(-?\d+\.\d+)', f_url)
                
                extracted = False
                for m in [m1, m2, m3, m4]:
                    if m:
                        st.session_state.cached_gmaps_lat = m.group(1)
                        st.session_state.cached_gmaps_lon = m.group(2)
                        st.session_state.gmaps_status_msg = f"📍 Link Dikenali! Latitude: **{m.group(1)}**, Longitude: **{m.group(2)}**"
                        extracted = True
                        break
                if not extracted:
                    st.session_state.gmaps_status_msg = "⚠️ Tidak dapat mengekstrak koordinat dari link tersebut."
                    st.session_state.cached_gmaps_lat = ""
                    st.session_state.cached_gmaps_lon = ""
        except Exception as e:
            st.session_state.gmaps_status_msg = f"⚠️ Gagal mengekstrak koordinat."
            st.session_state.cached_gmaps_lat = ""
            st.session_state.cached_gmaps_lon = ""
            
    if st.session_state.gmaps_status_msg and gmaps_link == st.session_state.cached_gmaps_link:
        if "📍" in st.session_state.gmaps_status_msg:
            st.success(st.session_state.gmaps_status_msg)
        else:
            st.warning(st.session_state.gmaps_status_msg)
            
    gmaps_lat = st.session_state.cached_gmaps_lat if gmaps_link == st.session_state.cached_gmaps_link else ""
    gmaps_lon = st.session_state.cached_gmaps_lon if gmaps_link == st.session_state.cached_gmaps_link else ""
            
    col5, col6 = st.columns(2)
    with col5:
        lat_baru = st.text_input("Latitude (Opsional)", value=gmaps_lat, placeholder="Contoh: -6.550")
    with col6:
        lon_baru = st.text_input("Longitude (Opsional)", value=gmaps_lon, placeholder="Contoh: 107.450")
        
    submit_input = st.button("Simpan & Masukkan Antrean", type="primary")
    
    if submit_input:
        if not nopel_baru or not pemohon_baru or not nop_baru:
            st.error("Nomor Pelayanan, Nama Pemohon, dan NOP wajib diisi!")
        else:
            existing_df = fetch_berkas()
            is_dup = False
            dup_msg = ""
            if not existing_df.empty:
                if nopel_baru in existing_df['nomor_pelayanan'].values:
                    is_dup = True
                    dup_msg = f"Nomor Pelayanan ({nopel_baru})"
                elif nop_baru in existing_df['nomor_nop'].values:
                    is_dup = True
                    dup_msg = f"NOP ({nop_baru})"
            
            if is_dup:
                st.error(f"❌ Gagal menyimpan! Berkas dengan {dup_msg} tersebut sudah pernah didaftarkan sebelumnya.")
                st.stop()
                
            import re
            nop_clean = re.sub(r'\D', '', nop_baru)
            kecamatan_baru = "TIDAK DIKETAHUI"
            kelurahan_baru = "TIDAK DIKETAHUI"
            
            formatted_nop = nop_baru
            if len(nop_clean) == 18:
                formatted_nop = f"{nop_clean[:2]}.{nop_clean[2:4]}.{nop_clean[4:7]}.{nop_clean[7:10]}.{nop_clean[10:13]}.{nop_clean[13:17]}.{nop_clean[17:]}"
            
            nop_baru = formatted_nop
            
            if len(nop_clean) >= 10:
                kode = nop_clean[4:10]
                ref_nop = load_referensi_nop()
                if kode in ref_nop:
                    kecamatan_baru = ref_nop[kode]['kecamatan']
                    kelurahan_baru = ref_nop[kode]['kelurahan']
                    st.success(f"Lokasi otomatis terdeteksi: Kecamatan {kecamatan_baru}, Kelurahan {kelurahan_baru}.")
                else:
                    st.warning("Peringatan: Kode Kecamatan/Kelurahan pada NOP tidak dikenali. Lokasi diset sebagai 'TIDAK DIKETAHUI'.")
            else:
                st.warning("Format NOP tidak valid (kurang dari 18 digit) atau salah. Lokasi tidak bisa dideteksi.")
            
            lat_val, lon_val = None, None
                
            if gmaps_link:
                import requests
                import re
                import urllib.parse
                try:
                    response = requests.get(gmaps_link, allow_redirects=True, timeout=7)
                    final_url = urllib.parse.unquote(response.url)
                    
                    m1 = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
                    m2 = re.search(r'search/(-?\d+\.\d+),\s*\+?(-?\d+\.\d+)', final_url)
                    m3 = re.search(r'q=(-?\d+\.\d+),\s*(-?\d+\.\d+)', final_url)
                    m4 = re.search(r'll=(-?\d+\.\d+),\s*(-?\d+\.\d+)', final_url)
                    
                    for m in [m1, m2, m3, m4]:
                        if m:
                            lat_val = float(m.group(1))
                            lon_val = float(m.group(2))
                            break
                except Exception as e:
                    st.warning(f"Gagal mengekstrak koordinat dari link Maps: {e}")
                    
            if lat_val is None and lon_val is None and lat_baru and lon_baru:
                try:
                    lat_val = float(lat_baru)
                    lon_val = float(lon_baru)
                except:
                    pass
            
            if lat_val is None or lon_val is None:
                import os, json
                try:
                    if os.path.exists('koordinat_desa.json'):
                        with open('koordinat_desa.json', 'r') as f:
                            kd = json.load(f)
                        k = f"{kecamatan_baru}_{kelurahan_baru}"
                        if k in kd:
                            lat_val = kd[k]['lat']
                            lon_val = kd[k]['lon']
                except Exception:
                    pass
                
                # Jaring pengaman mutlak agar TIDAK PERNAH error merah lagi
                if lat_val is None or lon_val is None:
                    # Titik tengah Purwakarta sebagai default jika semua gagal
                    lat_val, lon_val = -6.553618, 107.451278
                    st.warning(f"⚠️ Menggunakan titik koordinat default wilayah Purwakarta untuk Kelurahan {kelurahan_baru}.")
            if USE_MOCK_DATA:
                import uuid
                import datetime
                new_berkas = {
                    'id': str(uuid.uuid4()),
                    'nomor_pelayanan': nopel_baru,
                    'nomor_nop': nop_baru,
                    'nama_pemohon': pemohon_baru,
                    'tanggal_input': datetime.date.today().strftime('%Y-%m-%d'),
                    'is_urgent': urgensi_baru,
                    'keterangan_berkas': kategori_baru,
                    'kecamatan': kecamatan_baru,
                    'desa': kelurahan_baru,
                    'status_survey': 'Belum',
                    'lat': lat_val,
                    'lon': lon_val
                }
                if 'mock_berkas' not in st.session_state:
                    init_mock_data()
                st.session_state.mock_berkas.append(new_berkas)
                st.success(f"Berhasil! Berkas {nopel_baru} (Kel. {kelurahan_baru}) masuk ke Daftar Tunggu.")
            else:
                try:
                    db_berkas = {
                        'no_pelayanan': nopel_baru,
                        'kategori_berkas': kategori_baru,
                        'nomor_nop': nop_clean,
                        'nama_pemohon': pemohon_baru,
                        'mendesak': urgensi_baru,
                        'kecamatan': kecamatan_baru,
                        'kelurahan': kelurahan_baru,
                        'lokasi_map': gmaps_link,
                        'latitude': lat_val,
                        'longitude': lon_val,
                        'status_survey': 'Belum'
                    }
                    supabase.table('berkas').insert(db_berkas).execute()
                    st.cache_data.clear()
                    st.success(f"Berhasil! Berkas {nopel_baru} (Kel. {kelurahan_baru}) berhasil disimpan ke Database.")
                except Exception as e:
                    st.error(f"Gagal menyimpan ke database (Pastikan tabel 'berkas' sudah dibuat di SQL Editor). Error: {e}")


# --- TAB 1: PETA INTERAKTIF ---
with tab1:
    st.header("Peta Sebaran Berkas Verlap")
    referensi_wilayah = load_referensi()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kec_list = ["Semua"] + sorted(list(referensi_wilayah.keys())) if referensi_wilayah else ["Semua", "PURWAKARTA", "BOJONG", "JATILUHUR"]
        selected_kec = st.selectbox("Pilih Kecamatan", kec_list)
    with col2:
        if selected_kec != "Semua" and referensi_wilayah:
            desa_list = ["Semua"] + sorted(referensi_wilayah[selected_kec])
        else:
            desa_list = ["Semua"]
        selected_desa = st.selectbox("Pilih Kelurahan/Desa", desa_list)
    with col3:
        status_options = ["Semua", "Belum", "Dijadwalkan", "Sudah"]
        selected_status = st.selectbox("Status Survei", status_options)
    with col4:
        st.write("") # Spacer for alignment
        st.write("")
        only_urgent = st.checkbox("🚨 Hanya Berkas Urgent")
        
    df_berkas_raw = fetch_berkas(selected_kec, selected_status, only_urgent)
    if not df_berkas_raw.empty and selected_desa != "Semua":
        df_berkas_raw = df_berkas_raw[df_berkas_raw['desa'].str.upper() == selected_desa.upper()]
        
    kab_geojson = load_geojson("kab_purwakarta.geojson")
    
    # Fitur Validasi Koordinat (Menolak input di luar batas Purwakarta)
    if not df_berkas_raw.empty and kab_geojson and HAS_SHAPELY:
        kab_geom = shape(kab_geojson['features'][0]['geometry'])
        df_berkas_raw['is_valid'] = df_berkas_raw.apply(lambda r: kab_geom.contains(Point(r['lon'], r['lat'])), axis=1)
        df_berkas = df_berkas_raw[df_berkas_raw['is_valid'] == True].copy()
        
        luar_count = len(df_berkas_raw) - len(df_berkas)
        if luar_count > 0:
            st.error(f"🛑 **SISTEM KEAMANAN:** Menolak otomatis {luar_count} berkas inputan karena titik koordinatnya berada di LUAR batas administratif Kabupaten Purwakarta.")
    else:
        df_berkas = df_berkas_raw.copy()
    
    # Menentukan area mana yang "menyala" (fokus)
    geom_to_highlight = None
    bounds_to_fit = None
    
    kec_geojson = load_geojson("kecamatan_purwakarta.geojson")
    desa_geojson = load_geojson("kelurahan_purwakarta.geojson")
    
    if selected_desa != "Semua" and desa_geojson and HAS_SHAPELY:
        feature = get_feature_by_name(desa_geojson, selected_desa)
        if feature:
            geom_to_highlight = shape(feature['geometry'])
            bounds_to_fit = get_bounds_from_geom(geom_to_highlight)
    elif selected_kec != "Semua" and kec_geojson and HAS_SHAPELY:
        feature = get_feature_by_name(kec_geojson, selected_kec)
        if feature:
            geom_to_highlight = shape(feature['geometry'])
            bounds_to_fit = get_bounds_from_geom(geom_to_highlight)

    # Calculate center and zoom BEFORE creating map
    center_loc = BAPENDA_COORD
    zoom_level = 11
    
    valid_coords = pd.DataFrame()
    if not df_berkas.empty:
        valid_coords = df_berkas.copy()
        valid_coords['lat'] = pd.to_numeric(valid_coords['lat'], errors='coerce')
        valid_coords['lon'] = pd.to_numeric(valid_coords['lon'], errors='coerce')
        valid_coords = valid_coords.dropna(subset=['lat', 'lon'])
        valid_coords = valid_coords[(valid_coords['lat'] != 0) & (valid_coords['lon'] != 0)]
    
    if bounds_to_fit:
        center_loc = [(bounds_to_fit[0][0] + bounds_to_fit[1][0])/2, (bounds_to_fit[0][1] + bounds_to_fit[1][1])/2]
        zoom_level = 13
    else:
        # Default zoom to Purwakarta
        center_loc = BAPENDA_COORD
        zoom_level = 12

    # Inisialisasi Peta
    m = folium.Map(location=center_loc, zoom_start=zoom_level)

    # Highlight
    if geom_to_highlight:
        folium.GeoJson(
            geom_to_highlight.__geo_interface__,
            style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.1}
        ).add_to(m)

    # Paskan Kamera jika punya bounds to fit
    if bounds_to_fit:
        m.fit_bounds(bounds_to_fit)

    # 4. Marker for Bapenda Purwakarta
    folium.Marker(
        BAPENDA_COORD,
        popup="<b>Kantor Bapenda Purwakarta</b>",
        tooltip="Titik Awal (Kantor Bapenda)",
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(m)

    # 5. Route Optimization Line
    routes_dict = {}
    if selected_status in ["Semua", "Belum"] and not df_berkas.empty:
        df_belum = df_berkas[df_berkas['status_survey'] == 'Belum']
        if not df_belum.empty:
            routes_dict = optimize_multiple_routes(df_belum)
            
            colors = ['#f47820', '#17a2b8', '#28a745', '#dc3545', '#6f42c1', '#e83e8c', '#fd7e14', '#20c997']
            
            r_idx = 0
            for arah, route_list in routes_dict.items():
                r_color = colors[r_idx % len(colors)]
                route_coords = [BAPENDA_COORD] + [[p['lat'], p['lon']] for p in route_list]
                
                folium.PolyLine(
                    route_coords,
                    color=r_color,
                    weight=3,
                    opacity=0.8,
                    dash_array='10, 10',
                    tooltip=f"Rute {r_idx+1}"
                ).add_to(m)
                
                for i, p in enumerate(route_list):
                    folium.Marker(
                        [p['lat'], p['lon']],
                        icon=plugins.BeautifyIcon(
                            icon='arrow-down', icon_shape='marker',
                            number=i+1, border_color=r_color, text_color=r_color
                        )
                    ).add_to(m)
                r_idx += 1

    # 6. Render Berkas Markers (Non-Belum)
    for _, row in df_berkas.iterrows():
        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            if row['status_survey'] != 'Belum' or not row.get('is_urgent', False): # Urgent will be red anyway
                urgensi = "🔥 URGENT" if row.get('is_urgent') else "Normal"
                if row.get('is_urgent'):
                    color = 'red'
                    icon_tipe = 'warning-sign'
                else:
                    color = 'orange' if row['status_survey'] == 'Dijadwalkan' else 'green'
                    icon_tipe = 'info-sign'
                    
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=f"No. Pel: {row.get('nomor_pelayanan', '-')}<br>NOP: {format_nop_string(row['nomor_nop'])}<br>Tgl Input: {row.get('tanggal_input', '-')}<br>Urgensi: <b>{urgensi}</b><br>Kategori: {row.get('keterangan_berkas', '-')}<br>Status: {row['status_survey']}",

                    tooltip=row.get('nomor_pelayanan', format_nop_string(row['nomor_nop'])),
                    icon=folium.Icon(color=color, icon=icon_tipe)
                ).add_to(m)
            
    folium.LayerControl().add_to(m)
            
    dynamic_map_key = f"map_{selected_kec}_{selected_desa}_{selected_status}_{only_urgent}_{len(df_berkas)}"
    st_folium(m, width=1200, height=500, returned_objects=[], key=dynamic_map_key)
    
    if routes_dict:
        total_berkas = sum(len(r) for r in routes_dict.values())
        st.success(f"📌 Ditemukan {total_berkas} Berkas Belum Survei. Sistem telah membaginya menjadi {len(routes_dict)} rute berdasarkan kelompok 4 arah mata angin (Searah).")
        
        route_tabs = st.tabs([f"🚗 Rute {idx+1}" for idx in range(len(routes_dict))])
        for idx, (arah, route_list) in enumerate(routes_dict.items()):
            with route_tabs[idx]:
                st.subheader(f"Rute {idx+1} (Arah {arah})")
                
                # Format Data untuk Tampilan (Ramah Pengguna)
                df_display = pd.DataFrame(route_list)[['is_urgent', 'tanggal_input', 'nomor_pelayanan', 'keterangan_berkas', 'nomor_nop', 'nama_pemohon', 'desa', 'status_survey']]
                
                # Ubah boolean menjadi teks yang mudah dipahami
                df_display['is_urgent'] = df_display['is_urgent'].apply(lambda x: "🚨 Mendesak" if x else "Normal")
                
                # Ubah nama header kolom menjadi bahasa Indonesia formal
                df_display = df_display.rename(columns={
                    'is_urgent': 'Tingkat Urgensi',
                    'tanggal_input': 'Tgl. Masuk',
                    'nomor_pelayanan': 'No. Pelayanan',
                    'keterangan_berkas': 'Kategori Berkas',
                    'nomor_nop': 'Nomor NOP',
                    'nama_pemohon': 'Nama Pemohon',
                    'desa': 'Kelurahan/Desa',
                    'status_survey': 'Status'
                })
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
    elif df_berkas.empty:
        st.info("Tidak ada data berkas yang sesuai filter.")

# --- TAB 2, 3, 4 SAMA SEPERTI SEBELUMNYA ---
with tab2:
    st.header("Form Penjadwalan & Penugasan")
    df_pegawai = fetch_pegawai()
    df_berkas_belum = fetch_berkas(status="Belum")
    
    if not df_pegawai.empty and not df_berkas_belum.empty:
        st.info("💡 Pilih bundel rute yang disarankan dari Peta, atau biarkan 'Pilih Sendiri' untuk memilih berkas secara manual.")
        
        # 1. Hitung ulang rute untuk mendapatkan bundel
        routes_dict = optimize_multiple_routes(df_berkas_belum)
        
        bundle_options = ["Pilih Sendiri (Manual)"]
        bundle_data = {}
        for r_idx, (arah, route_list) in enumerate(routes_dict.items()):
            b_name = f"Bundel Rute {r_idx+1} (Arah {arah}) - {len(route_list)} Berkas"
            bundle_options.append(b_name)
            bundle_data[b_name] = [b['id'] for b in route_list]
            
        selected_bundle = st.selectbox("Pilih Bundel Rute (Otomatis)", options=bundle_options)
        
        default_selected = []
        if selected_bundle != "Pilih Sendiri (Manual)":
            default_selected = bundle_data[selected_bundle]
            
        # Pemetaan ID ke Label Display
        berkas_options = df_berkas_belum['id'].tolist()
        berkas_labels = {row['id']: f"{row.get('nomor_pelayanan', '-')} / {format_nop_string(row['nomor_nop'])} - {row['nama_pemohon']} ({row.get('keterangan_berkas', '-')})" for _, row in df_berkas_belum.iterrows()}
        pegawai_dict = {row['id']: f"{row['nama_pegawai'].split(',')[0]} - {row.get('nip', '-')} ({row.get('jabatan', '-')})" for _, row in df_pegawai.iterrows()}
        
        with st.form("form_penugasan"):
            selected_berkas = st.multiselect(
                "Pilih Berkas (No. Pelayanan / NOP - Nama)", 
                options=berkas_options,
                default=default_selected,
                format_func=lambda x: berkas_labels[x]
            )
            
            selected_pegawai = st.multiselect(
                "Pilih 2 Pegawai (Tim Survei)", 
                options=list(pegawai_dict.keys()), 
                format_func=lambda x: pegawai_dict[x],
                max_selections=2
            )
            
            tgl_survei = st.date_input("Rencana Tanggal Survei", datetime.date.today())
            nomor_surat = st.text_input("Nomor Surat (3 digit)", value="340", max_chars=3)
            
            submit_btn = st.form_submit_button("Tugaskan & Jadwalkan")
            
        # PROSES DILUAR FORM
        if submit_btn:
            if not selected_berkas:
                st.error("Mohon pilih setidaknya 1 berkas!")
            elif len(selected_pegawai) != 2:
                st.error("Mohon pilih tepat 2 pegawai untuk diberangkatkan bersama!")
            else:
                if USE_MOCK_DATA:
                    for b_id in selected_berkas:
                        for b in st.session_state.mock_berkas:
                            if b['id'] == b_id:
                                b['status_survey'] = 'Dijadwalkan'
                                b['petugas_1'] = selected_pegawai[0] if len(selected_pegawai) > 0 else None
                                b['petugas_2'] = selected_pegawai[1] if len(selected_pegawai) > 1 else None
                    st.success("Penugasan berhasil! Status 1 atau lebih berkas telah diupdate menjadi 'Dijadwalkan'.")
                else:
                    for b_id in selected_berkas:
                        update_data = {
                            "status_survey": "Dijadwalkan",
                            "petugas_survey": " & ".join(selected_pegawai)
                        }
                        try:
                            supabase.table("berkas").update(update_data).eq("id", b_id).execute()
                        except Exception as e:
                            st.error(f"Gagal update database: {e}")
                    st.success("Penugasan berhasil disimpan! Status berkas telah diperbarui menjadi 'Dijadwalkan'.")
                
                nama_petugas = " & ".join([pegawai_dict[p] for p in selected_pegawai])
                st.success(f"""
**SURAT TUGAS VERIFIKASI LAPANGAN**

Tim Bertugas: **{nama_petugas}**
Tanggal Pelaksanaan: **{tgl_survei.strftime('%d %B %Y')}**

Daftar Objek Pajak (No. Pelayanan / NOP):
""")
                for b_id in selected_berkas:
                    st.write(f"- {berkas_labels[b_id]}")
                    
                # GET ACTUAL DATA FOR PDF
                if USE_MOCK_DATA:
                    berkas_list_pdf = [b for b in st.session_state.mock_berkas if b['id'] in selected_berkas]
                else:
                    berkas_list_pdf = df_berkas_belum[df_berkas_belum['id'].isin(selected_berkas)].to_dict('records')
                    
                pegawai_list_pdf = df_pegawai[df_pegawai['id'].isin(selected_pegawai)].to_dict('records')
                
                st.write("---")
                st.write("Silakan download Surat Perintah untuk masing-masing berkas di bawah ini:")
                
                try:
                    base_nomor_surat = int(nomor_surat)
                except ValueError:
                    base_nomor_surat = nomor_surat
                
                cols = st.columns(2)
                for i, b in enumerate(berkas_list_pdf):
                    single_b = [b]
                    
                    if isinstance(base_nomor_surat, int):
                        current_nomor_surat = str(base_nomor_surat + i).zfill(len(str(nomor_surat)))
                    else:
                        current_nomor_surat = f"{nomor_surat}-{i+1}"
                        
                    pdf_bytes = generate_surat_perintah(single_b, pegawai_list_pdf, tgl_survei, current_nomor_surat)
                    
                    with cols[i % 2]:
                        st.download_button(
                            label=f"📄 Surat Tugas: {b.get('nomor_pelayanan', b['nomor_nop'])}",
                            data=pdf_bytes,
                            file_name=f"Surat_Perintah_{b.get('nomor_pelayanan', b['nomor_nop']).replace('.','_')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            key=f"dl_btn_{b['id']}_{i}"
                        )
                
                if not USE_MOCK_DATA:
                    st.cache_data.clear()
    else:
        st.warning("Data pegawai atau berkas (Belum Survei) masih kosong.")

with tab3:
    st.header("📊 Beban Kerja Pegawai (Workload Balancing)")
    
    df_berkas_all = fetch_berkas()
    df_pegawai = fetch_pegawai()
    
    pegawai_workload = []
    
    for _, peg in df_pegawai.iterrows():
        peg_id = peg['id']
        peg_nama = peg['nama_pegawai']
        
        ongoing = 0
        selesai = 0
        
        if not df_berkas_all.empty:
            mask_peg = pd.Series(False, index=df_berkas_all.index)
            
            if 'petugas_survey' in df_berkas_all.columns:
                df_berkas_all['petugas_survey'] = df_berkas_all['petugas_survey'].fillna('')
                # Use regex \b to match exact peg-1 and not peg-10
                import re
                escaped_peg_id = re.escape(str(peg_id))
                mask_peg = mask_peg | df_berkas_all['petugas_survey'].str.contains(rf'\b{escaped_peg_id}\b', regex=True, na=False)
                
            if 'petugas_1' in df_berkas_all.columns:
                mask_peg = mask_peg | (df_berkas_all['petugas_1'] == peg_id) | (df_berkas_all['petugas_2'] == peg_id)
                
            berkas_peg = df_berkas_all[mask_peg]
            ongoing = len(berkas_peg[berkas_peg['status_survey'] == 'Dijadwalkan'])
            selesai = len(berkas_peg[berkas_peg['status_survey'] == 'Sudah'])
            
        pegawai_workload.append({
            'Nama Pegawai': peg_nama.split(',')[0].title(),
            'Dijadwalkan (Proses)': ongoing,
            'Selesai (Selesai)': selesai,
            'Total': ongoing + selesai
        })
        
    df_workload = pd.DataFrame(pegawai_workload)
    df_workload = df_workload.sort_values(by='Total', ascending=False).reset_index(drop=True)
    
    # Tambahkan Medali untuk Top 3
    for idx in range(min(3, len(df_workload))):
        if df_workload.loc[idx, 'Total'] > 0:
            medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉"
            df_workload.loc[idx, 'Nama Pegawai'] = f"{medal} {df_workload.loc[idx, 'Nama Pegawai']}"
            
    # Tampilkan Saran Penugasan
    lowest_workload_df = df_workload.sort_values(by='Total', ascending=True).head(3)
    if not lowest_workload_df.empty:
        lowest_names = lowest_workload_df['Nama Pegawai'].tolist()
        # Clean up medals if they accidentally got ones (e.g., if everyone has 0 or 1)
        clean_names = [n.replace("🥇 ", "").replace("🥈 ", "").replace("🥉 ", "") for n in lowest_names]
        st.info(f"💡 **Saran Penugasan:** Pertimbangkan menugaskan **{', '.join(clean_names)}** karena beban survei mereka paling sedikit saat ini.")
    
    import plotly.express as px
    df_melt = df_workload.melt(id_vars='Nama Pegawai', value_vars=['Dijadwalkan (Proses)', 'Selesai (Selesai)'], var_name='Status', value_name='Jumlah Berkas')
    
    fig = px.bar(
        df_melt, 
        x='Nama Pegawai', 
        y='Jumlah Berkas', 
        color='Status',
        title='Distribusi Beban Kerja Pegawai',
        template='plotly_white',
        text='Jumlah Berkas',
        color_discrete_map={'Dijadwalkan (Proses)': '#f59e0b', 'Selesai (Selesai)': '#10b981'}
    )
    
    fig.update_layout(xaxis_title="", yaxis_title="Jumlah Berkas", barmode='stack')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_workload, use_container_width=True, hide_index=True)

with tab4:
    st.header("📱 Laporan Verifikasi Lapangan")
    df_berkas_jadwal = fetch_berkas(status="Dijadwalkan")
    
    if not df_berkas_jadwal.empty:
        with st.form("form_lapangan"):
            lapangan_options = df_berkas_jadwal['id'].tolist()
            lapangan_labels = {row['id']: f"{row.get('nomor_pelayanan', '-')} / {format_nop_string(row['nomor_nop'])} - {row['nama_pemohon']} ({row.get('keterangan_berkas', '-')})" for _, row in df_berkas_jadwal.iterrows()}
            
            selected_lapangan = st.selectbox(
                "Pilih Berkas", 
                options=lapangan_options,
                format_func=lambda x: lapangan_labels[x],
                index=None,
                placeholder="🔍 Ketik NOP, No. Pelayanan, atau Nama untuk mencari..."
            )
            
            catatan = st.text_area("Catatan Kondisi Riil Lapangan")
            st.markdown("**Titik Koordinat (GPS)**")
            st.write("Silakan klik tombol di bawah untuk merekam koordinat lokasi survei Anda.")
            location = streamlit_geolocation()
            
            if location and location.get('latitude'):
                st.success(f"📍 Tersimpan: {location['latitude']}, {location['longitude']}")
            
            submit_lapangan = st.form_submit_button("Selesaikan Survei")
            if submit_lapangan:
                if not selected_lapangan:
                    st.error("Mohon pilih berkas terlebih dahulu!")
                else:
                    try:
                        update_data = {'status_survey': 'Sudah'}
                        if catatan:
                            update_data['catatan_petugas'] = catatan
                        if location and location.get('latitude'):
                            update_data['lat_petugas'] = location['latitude']
                            update_data['lon_petugas'] = location['longitude']
                            
                        supabase.table('berkas').update(update_data).eq('id', selected_lapangan).execute()
                        st.cache_data.clear()
                        st.success("✅ Laporan lapangan berhasil disubmit dan tersimpan di database!")
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan laporan: {e}")
    else:
        st.info("Tidak ada berkas yang berstatus 'Dijadwalkan'.")

with tab5:
    st.header("🔍 Tracking Verlap Berkas PBB-P2 / BPHTB")
    st.write("Cari dan lacak status berkas verifikasi lapangan secara real-time.")
    
    df_all = fetch_berkas()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Cari Nomor (Pelayanan/NOP) / Nama:", placeholder="Ketik spesifik...")
    with col2:
        kec_list = ["Semua"] + sorted([k for k in df_all['kecamatan'].unique() if pd.notna(k)])
        filter_kec = st.selectbox("Filter Kecamatan:", kec_list)
    with col3:
        status_list = ["Semua", "Belum", "Dijadwalkan", "Sudah"]
        filter_status = st.selectbox("Filter Status Survei:", status_list, format_func=lambda x: {
            "Semua": "Semua Status",
            "Belum": "⏳ Menunggu Jadwal",
            "Dijadwalkan": "🏃 Sedang Proses",
            "Sudah": "✅ Selesai"
        }.get(x, x))
        
    result = df_all.copy()
    if search_query:
        mask = result['nomor_pelayanan'].astype(str).str.contains(search_query, case=False, na=False) | result['nomor_nop'].astype(str).str.contains(search_query, case=False, na=False) | result['nama_pemohon'].astype(str).str.contains(search_query, case=False, na=False)
        result = result[mask]
    if filter_kec != "Semua":
        result = result[result['kecamatan'] == filter_kec]
    if filter_status != "Semua":
        result = result[result['status_survey'] == filter_status]
        
    items_per_page = 10
    total_pages = max(1, (len(result) - 1) // items_per_page + 1)
    
    col_info, col_page = st.columns([3, 1])
    with col_info:
        st.markdown(f"##### 📋 Menampilkan Total {len(result)} Berkas")
    with col_page:
        if total_pages > 1:
            page = st.number_input("Halaman", min_value=1, max_value=total_pages, step=1)
        else:
            page = 1
            
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    result_page = result.iloc[start_idx:end_idx]
    
    if not result_page.empty:
        df_show = result_page[['nomor_pelayanan', 'nomor_nop', 'nama_pemohon', 'keterangan_berkas', 'kecamatan', 'desa', 'status_survey', 'tanggal_input']].copy()
        
        df_show = df_show.rename(columns={
            'nomor_pelayanan': 'No. Pelayanan',
            'nomor_nop': 'NOP',
            'nama_pemohon': 'Nama Pemohon',
            'keterangan_berkas': 'Kategori',
            'kecamatan': 'Kecamatan',
            'desa': 'Kelurahan',
            'status_survey': 'Status Survei',
            'tanggal_input': 'Tgl Input'
        })
        
        def format_status(val):
            if val == 'Belum': return '⏳ Menunggu Jadwal'
            if val == 'Dijadwalkan': return '🏃 Sedang Proses'
            if val == 'Sudah': return '✅ Selesai'
            return val
            
        df_show['Status Survei'] = df_show['Status Survei'].apply(format_status)
        
        def highlight_status(s):
            if s['Status Survei'] == '✅ Selesai':
                return ['background-color: #d1fae5; color: #065f46'] * len(s)
            elif s['Status Survei'] == '🏃 Sedang Proses':
                return ['background-color: #fef08a; color: #854d0e'] * len(s)
            else:
                return [''] * len(s)
                
        styled_df = df_show.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("Pencarian tidak ditemukan. Pastikan Nomor Pelayanan atau NOP sudah diketik dengan benar.")

    # === DETAIL SECTION ===
    st.write("---")
    st.subheader("🔍 Detail Laporan Petugas (Untuk Berkas Selesai)")
    
    # We use df_all instead of result_page because result_page only has a few columns
    df_sudah = df_all[df_all['status_survey'] == 'Sudah']
    if not df_sudah.empty:
        detail_options = df_sudah['id'].tolist()
        detail_labels = {row['id']: f"{row.get('nomor_pelayanan', '-')} / {format_nop_string(row['nomor_nop'])} - {row['nama_pemohon']}" for _, row in df_sudah.iterrows()}
        
        selected_detail = st.selectbox(
            "Pilih Berkas yang sudah selesai:", 
            options=detail_options,
            format_func=lambda x: detail_labels[x],
            index=None,
            placeholder="🔍 Ketik NOP atau Nama untuk mencari..."
        )
        
        if selected_detail:
            row_detail = df_sudah[df_sudah['id'] == selected_detail].iloc[0]
            
            col_det1, col_det2 = st.columns(2)
            with col_det1:
                st.info(f"**📝 Catatan Lapangan:**\n\n{row_detail.get('catatan_petugas', 'Tidak ada catatan.')}")
            
            with col_det2:
                lat_p = row_detail.get('lat_petugas')
                lon_p = row_detail.get('lon_petugas')
                if pd.notnull(lat_p) and pd.notnull(lon_p):
                    st.success(f"**📍 Koordinat Petugas:**\n\n{lat_p}, {lon_p}")
                    # Show mini map
                    df_map = pd.DataFrame({'lat': [float(lat_p)], 'lon': [float(lon_p)]})
                    st.map(df_map, zoom=15)
                else:
                    st.warning("Petugas tidak melampirkan titik koordinat GPS.")
    else:
        st.info("Belum ada berkas yang selesai disurvei untuk ditampilkan detailnya.")


    st.write("---")
    st.subheader("🗑️ Hapus Berkas")
    with st.expander("Klik untuk menghapus berkas dari sistem"):
        st.warning("Peringatan: Berkas yang dihapus tidak dapat dikembalikan.")
        del_nopel = st.text_input("Masukkan Nomor Pelayanan yang ingin dihapus:")
        
        if del_nopel:
            # Cari data berdasarkan nomor pelayanan di dataframe yang sudah ada (df_all)
            df_to_delete = df_all[df_all['nomor_pelayanan'].astype(str).str.strip() == str(del_nopel).strip()]
            
            if not df_to_delete.empty:
                b_del = df_to_delete.iloc[0]
                st.info(f"**Berkas Ditemukan!**\n\n- **Nama Pemohon:** {b_del['nama_pemohon']}\n- **NOP:** {format_nop_string(b_del['nomor_nop'])}\n- **Kelurahan/Desa:** {b_del.get('desa', '-')}\n- **Kategori:** {b_del.get('keterangan_berkas', '-')}\n- **Status Survei:** {b_del['status_survey']}")
                
                if st.button("⚠️ Ya, Hapus Berkas Ini Secara Permanen", type="primary", use_container_width=True):
                    if USE_MOCK_DATA:
                        original_len = len(st.session_state.mock_berkas)
                        st.session_state.mock_berkas = [b for b in st.session_state.mock_berkas if str(b['nomor_pelayanan']).strip() != str(del_nopel).strip()]
                        if len(st.session_state.mock_berkas) < original_len:
                            st.success(f"✅ Berkas dengan Nomor Pelayanan {del_nopel} berhasil dihapus.")
                            import time
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("❌ Nomor Pelayanan tidak ditemukan.")
                    else:
                        try:
                            # Ingat: kolom di Supabase namanya no_pelayanan
                            res = supabase.table('berkas').delete().eq('no_pelayanan', str(del_nopel).strip()).execute()
                        except:
                            res = type('obj', (object,), {'data': []})
                        if hasattr(res, 'data') and len(res.data) > 0:
                            st.cache_data.clear()
                            st.success(f"✅ Berkas dengan Nomor Pelayanan {del_nopel} berhasil dihapus.")
                            import time
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("❌ Berkas gagal dihapus atau tidak ditemukan di database.")
            else:
                st.warning("Nomor Pelayanan tidak ditemukan di sistem. Pastikan diketik dengan benar.")

    st.write("---")
    st.subheader("⚠️ Reset Sistem")
    with st.expander("Klik untuk menghapus SELURUH berkas dari sistem"):
        st.error("PERHATIAN: Tindakan ini akan MENGHAPUS SEMUA DATA BERKAS secara permanen. Gunakan hanya saat akan memulai penerapan sistem baru.")
        confirm_reset = st.text_input("Ketik 'RESET' untuk mengonfirmasi:")
        if st.button("🗑️ Hapus Semua Data", type="primary", use_container_width=True):
            if confirm_reset == 'RESET':
                if USE_MOCK_DATA:
                    st.session_state.mock_berkas = []
                    st.success("✅ Semua data mock berhasil dihapus.")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    try:
                        supabase.table('berkas').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                        st.cache_data.clear()
                        st.success("✅ Semua data berhasil dihapus dari sistem.")
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Gagal menghapus data: {e}")
            else:
                st.warning("Silakan ketik 'RESET' dengan huruf kapital pada kolom di atas untuk mengonfirmasi.")
