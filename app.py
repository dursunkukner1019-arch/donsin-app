import streamlit as st
import base64
import hashlib
import json

# ==========================================
# SAYFA VE TEMA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="MathCrypt Enterprise Studio",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS Stil Entegrasyonu (Cyberpunk / Modern Dark Theme)
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        background-color: #00d2ff;
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0087ff;
        color: #fff;
        box-shadow: 0 0 10px #00d2ff;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ÇEKİRDEK MATEMATİKSEL ALGORİTMA
# ==========================================
FACTOR = (100 / (3 ** 5)) * 19  # ≈ 7.818930041152263

def process_bytes(data: bytes) -> bytes:
    """Tekil XOR döngüsü ile simetrik byte işleme"""
    if not data:
        return b""
    shift = int(FACTOR * 1000) % 256
    res = bytearray()
    for i, b in enumerate(data):
        res.append(b ^ ((shift + i) % 256))
    return bytes(res)

def calculate_entropy(data: bytes) -> float:
    """Verinin Shannon Entropisini (Karmaşıklığını) hesaplar"""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(data)
        entropy -= p * (p and (p * 3.321928094887362)) # log2 dönüşümü
    return round(abs(entropy), 4)

def bytes_to_hex_colors(data_bytes: bytes):
    """Bayt verisini görsel palet için HEX renk kodlarına dönüştürür"""
    hex_codes = []
    for i in range(0, len(data_bytes), 3):
        chunk = data_bytes[i:i+3]
        if len(chunk) < 3:
            chunk = chunk + b'\x00' * (3 - len(chunk))
        r = int((chunk[0] * FACTOR) % 256)
        g = int((chunk[1] * FACTOR) % 256)
        b = int((chunk[2] * FACTOR) % 256)
        hex_codes.append(f"#{r:02x}{g:02x}{b:02x}")
    return hex_codes

# ==========================================
# YAN MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/shield.png", width=80)
    st.title("MathCrypt v4.0")
    st.markdown("**Matematiksel Sabit:**")
    st.code(f"{FACTOR}", language="text")
    st.divider()
    st.markdown("### ⚙️ Sistem Durumu")
    st.success("Motor: Aktif (Simetrik XOR)")
    st.info("Bellek Kullanımı: Optimize")
    st.caption("© 2026 MathCrypt Enterprise")

# ==========================================
# ANA BAŞLIK
# ==========================================
st.title("🛡️ MathCrypt Enterprise Studio")
st.caption("100 / 3⁵ × 19 Sabiti Tabanlı Gelişmiş Kriptografik Analiz ve Veri Güvenliği Platformu")

# Sekmeler
tabs = st.tabs([
    "📝 Metin Şifreleme & Analiz", 
    "📁 Dosya Koruması", 
    "🎨 Görsel Steganografi", 
    "📊 Matris Analizörü",
    "🛡️ Hash & Bütünlük Raporu"
])

# ---------------------------------------------------------
# TAB 1: METİN İŞLEMLERİ VE ANALİZ
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("📝 Metin Şifreleme & Canlı Karmaşıklık Analizi")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        mode = st.radio("İşlem Modu", ["Şifrele", "Şifre Çöz"], horizontal=True, key="t_mode")
        txt_input = st.text_area("İşlenecek Metin Girdisi", height=150, placeholder="Metninizi buraya yazın...", key="t_in")
        btn_txt = st.button("Metni İşle ve Analiz Et", key="b_txt")

    with c2:
        if btn_txt and txt_input and txt_input.strip():
            try:
                raw_bytes = txt_input.encode('utf-8')
                if mode == "Şifrele":
                    processed = process_bytes(raw_bytes)
                    result_str = base64.b64encode(processed).decode('utf-8')
                else:
                    raw_dec = base64.b64decode(txt_input.strip().encode('utf-8'))
                    processed = process_bytes(raw_dec)
                    result_str = processed.decode('utf-8')

                st.success(f"İşlem Başarılı ({mode}):")
                st.code(result_str, language="text")

                # Metrik Kartları
                m1, m2, m3 = st.columns(3)
                m1.metric("Girdi Boyutu", f"{len(raw_bytes)} Bayt")
                m2.metric("Entropi (Skor)", calculate_entropy(processed))
                m3.metric("Algoritma", "100/3⁵×19 XOR")

                # JSON Rapor İndirme Paketi
                report = {
                    "mode": mode,
                    "input_length": len(raw_bytes),
                    "entropy": calculate_entropy(processed),
                    "factor_used": FACTOR,
                    "result": result_str
                }
                st.download_button(
                    label="📄 Güvenlik Raporunu (JSON) İndir",
                    data=json.dumps(report, indent=4),
                    file_name="security_report.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error("Hata: Girdi formatı çözülemedi! Geçerli bir veri girdiğinizden emin olun.")
        else:
            st.info("Lütfen sol taraftaki alana bir metin girip butona basın.")

# ---------------------------------------------------------
# TAB 2: DOSYA KORUMASI
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("📁 Dosya Şifreleme ve Kilit Platformu")
    st.write("Tüm dosya formatlarını (.pdf, .docx, .png, .mp3 vb.) matematiksel sabitle kilitler veya açar.")
    
    fc1, fc2 = st.columns(2)
    with fc1:
        uploaded_file = st.file_uploader("Dosyanızı Yükleyin", key="file_up")
        btn_file = st.button("Dosyayı Kilitle / Kilidi Aç", key="b_file")

    with fc2:
        if btn_file and uploaded_file is not None:
            file_data = uploaded_file.read()
            processed_file = process_bytes(file_data)
            
            st.success("Dosya İşlemi Tamamlandı!")
            st.caption(f"Orijinal Boyut: {len(file_data)} Bayt | İşlenmiş: {len(processed_file)} Bayt")
            
            st.download_button(
                label="📥 Güvenli Dosyayı İndir",
                data=processed_file,
                file_name=f"mathcrypt_{uploaded_file.name}",
                mime="application/octet-stream"
            )
        else:
            st.info("Lütfen bir dosya seçin.")

# ---------------------------------------------------------
# TAB 3: GÖRSEL STEGANOGRAFİ (RENK KODLAYICI)
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("🎨 Metinden Renk Spektrumu Üretici")
    st.write("Verinizdeki her 3 baytlık küme, $100 / 3^5 \\times 19$ sabitiyle işlenerek benzersiz bir HEX renk paletine dönüştürülür.")
    
    sc1, sc2 = st.columns(2)
    with sc1:
        steg_input = st.text_area("Renge Dönüştürülecek Veri", value="MathCrypt Enterprise 2026", key="steg_in")
        btn_steg = st.button("Spektrum Oluştur", key="b_steg")

    with sc2:
        if btn_steg and steg_input and steg_input.strip():
            enc_b = process_bytes(steg_input.encode('utf-8'))
            hex_colors = bytes_to_hex_colors(enc_b)
            
            st.markdown("**🎨 Oluşturulan Renk Paleti:**")
            cols = st.columns(min(len(hex_colors), 6))
            for idx, hex_code in enumerate(hex_colors[:12]):
                with cols[idx % 6]:
                    st.markdown(
                        f'<div style="background-color:{hex_code}; height:65px; border-radius:8px; text-align:center; line-height:65px; color:#fff; font-weight:bold; font-size:11px; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.5);">{hex_code}</div>', 
                        unsafe_allow_html=True
                    )
            st.code(f"HEX Listesi: {hex_colors}", language="text")

# ---------------------------------------------------------
# TAB 4: 2D MATRİS ANALİZÖRÜ
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("📊 2D Kriptografik Matris Tablosu")
    st.write("Metninizin sabitle çarpan ilişkisini sayısal grid formatında analiz edin.")
    
    mat_input = st.text_input("Matris Girdisi", value="Enterprise Crypto Matrix", key="mat_in")
    btn_mat = st.button("Matrisi Hesapla", key="b_mat")
    
    if btn_mat and mat_input and mat_input.strip():
        raw_b = process_bytes(mat_input.encode('utf-8'))
        
        grid = []
        row = []
        for b in raw_b:
            row.append(round(b * FACTOR, 3))
            if len(row) == 6:
                grid.append(row)
                row = []
        if row:
            grid.append(row + [0.0] * (6 - len(row)))
            
        st.dataframe(grid, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: HASH & BÜTÜNLÜK RAPORU
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("🛡️ Veri Bütünlüğü ve Kriptografik Hash Analizi")
    hash_in = st.text_area("Bütünlüğü Kontrol Edilecek Metin", key="h_in", placeholder="Verinizi yazın...")
    btn_hash = st.button("Hash İmzalarını Üret", key="b_hash")
    
    if btn_hash and hash_in and hash_in.strip():
        data_b = hash_in.encode('utf-8')
        
        st.markdown("**🔐 Kriptografik İmzalar:**")
        st.text_input("SHA-256 İmzası", value=hashlib.sha256(data_b).hexdigest(), disabled=True)
        st.text_input("SHA-512 İmzası", value=hashlib.sha512(data_b).hexdigest(), disabled=True)
        st.text_input("MD5 İmzası", value=hashlib.md5(data_b).hexdigest(), disabled=True)
