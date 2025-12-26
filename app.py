import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- 1. Konfigurasi Halaman ---
st.set_page_config(
    page_title="Dynocard AI Analyzer",
    page_icon="🛢️",
    layout="wide"
)

# --- 2. CSS Kustom ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #FF4B4B; color: white; border-radius: 5px; }
    .metric-container { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sidebar Konfigurasi ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Prioritas: Cek Secrets (Cloud) atau Input Manual
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("API Key terdeteksi secara otomatis.")
    else:
        api_key = st.text_input("Masukkan Google Gemini API Key", type="password")
        st.info("Dapatkan API Key di: [AI Studio](https://aistudio.google.com/)")
    
    st.divider()
    st.subheader("Panduan Visual Dynocard")
    st.caption("Bentuk geometri yang dianalisa AI:")
    st.markdown("""
    - **Normal:** Jajar genjang penuh.
    - **Gas Interference:** Downstroke melengkung.
    - **Fluid Pound:** Terpotong vertikal.
    - **Leaking Valves:** Sudut membulat.
    - **Parted Rod:** Garis horizontal.
    """)


# --- 4. Fungsi Analisa AI ---
def analyze_dynocard(image, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # Konfigurasi Model (Force JSON Mode)
        # model = genai.GenerativeModel('gemini-1.5-flash')
        # model = genai.GenerativeModel('gemini-1.5-pro')
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        Bertindaklah sebagai Senior Petroleum Engineer. Analisa gambar Sucker Rod Pump (SRP) Dynamometer Card berikut.
        
        Identifikasi kondisi sumur berdasarkan bentuk kurva:
        1. Normal: Full parallelogram.
        2. Gas Interference: Convex curves on downstroke.
        3. Fluid Pound: Sharp/sudden drop on downstroke due to low fluid level.
        4. Leaking Valves: Rounded corners.
        5. Parted Rod: Flat horizontal line.

        OUTPUT HARUS DALAM FORMAT JSON RAW:
        {
            "condition": "Salah satu kategori di atas",
            "confidence_score": 0-100,
            "analysis_summary": "Penjelasan teknis singkat (max 2 kalimat)",
            "load_estimation": {
                "max_load": number atau null,
                "min_load": number atau null,
                "unit": "lbs"
            },
            "recommendation": "Tindakan perbaikan spesifik"
        }
        """

        response = model.generate_content([prompt, image])
        # Membersihkan output dari markdown jika ada
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    
    except Exception as e:
        return {"error": str(e)}

# --- 5. Layout Utama ---
st.title("🛢️ Dynocard AI Analyzer")
st.markdown("Analisa Kerusakan Sumur SRP Berbasis Computer Vision & AI")
st.divider()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📤 Input Dynocard")
    uploaded_file = st.file_uploader("Pilih file gambar (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="File yang diunggah", use_container_width=True)

with col2:
    st.subheader("📊 Hasil Diagnosa AI")
    
    if uploaded_file:
        if st.button("🔍 Mulai Analisa Sekarang"):
            if not api_key:
                st.error("⚠️ Silakan masukkan API Key di sidebar!")
            else:
                with st.spinner('AI sedang memproses geometri kurva...'):
                    result = analyze_dynocard(img, api_key)
                    
                    if "error" in result:
                        st.error(f"Terjadi kesalahan: {result['error']}")
                    else:
                        # 1. Status & Confidence
                        cond = result.get("condition", "Unknown")
                        color = "green" if cond == "Normal" else "orange" if cond == "Gas Interference" else "red"
                        
                        st.markdown(f"### Kondisi: :{color}[{cond}]")
                        st.progress(result.get("confidence_score", 0) / 100)
                        
                        # 2. Ringkasan
                        st.info(f"**Analisa Engineer:** {result.get('analysis_summary')}")
                        
                        # 3. Metrik Beban
                        load = result.get("load_estimation", {})
                        m1, m2 = st.columns(2)
                        unit = load.get("unit", "lbs")
                        with m1:
                            st.metric("Max Load", f"{load.get('max_load') or 'N/A'} {unit}")
                        with m2:
                            st.metric("Min Load", f"{load.get('min_load') or 'N/A'} {unit}")
                        
                        # 4. Rekomendasi
                        st.warning(f"**Rekomendasi:** {result.get('recommendation')}")
                        
                        # 5. Raw Data
                        with st.expander("Lihat Data Teknis (JSON)"):
                            st.json(result)
    else:
        st.info("Silakan unggah gambar dynocard untuk melihat analisa.")

# --- 6. Footer ---
st.divider()

st.caption("© 2024 Aruna Dynacard Analyzer | Gunakan hasil ini sebagai referensi awal sebelum pengecekan lapangan.")






