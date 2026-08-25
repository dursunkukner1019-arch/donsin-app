import streamlit as st
import base64
import struct

# ==========================================
# SAYFA VE TEMA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="KÜKNER Crypto Studio Pro",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Görsel Stil Entegrasyonu (Modern KÜKNER Teması)
st.markdown("""
<style>
    .main { background-color: #0b0e14; }
    .stButton>button { 
        background-color: #00d2ff; 
        color: #000; 
        font-weight: bold; 
        border-radius: 8px; 
        width: 100%;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #0087ff; 
        color: #fff; 
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); 
    }
    .kukner-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 100 / 3⁵ × 19 Matematiksel Sabiti
FACTOR = (100 / (3 ** 5)) * 19  # ≈ 7.818930041152263

# ==========================================
# EBCED TABLOLARI (TR / AR / OSM)
# ==========================================
EBCED_ARAPCA = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ء': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 
    'ح': 8, 'ط': 9, 'ي': 10, 'ى': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 
    'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 
    'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000, 'پ': 2, 'چ': 3, 'ژ': 7, 'گ': 20
}

EBCED_TURKCE = {
    'a': 1, 'b': 2, 'c': 3, 'ç': 3, 'd': 4, 'e': 5, 'f': 80, 'g': 20, 'ğ': 1000,
    'h': 8, 'ı': 10, 'i': 10, 'j': 7, 'k': 20, 'l': 30, 'm': 40, 'n': 50, 'o': 6,
    'ö': 6, 'p': 2, 'r': 200, 's': 60, 'ş': 300, 't': 400, 'u': 6, 'ü': 6, 'v': 6,
    'y': 10, 'z': 7
}

# ==========================================
# ÇEKİRDEK FONKSİYONLAR
# ==========================================
def process_bytes(data: bytes) -> bytes:
    """Tekil XOR döngüsü ile simetrik byte işleme"""
    if not data: return b""
    shift = int(FACTOR * 1000) % 256
    res = bytearray()
    for i, b in enumerate(data):
        res.append(b ^ ((shift + i) % 256))
    return bytes(res)

def generate_audio_digital(text_data: str):
    """Metin verisini %100 kayıpsız dijital ses paketine çevirir"""
    raw_bytes = process_bytes(text_data.encode('utf-8'))
    sample_rate = 8000
    samples_per_byte = 50
    audio_samples = []
    
    for b in raw_bytes:
        val = int((b - 128) * 200)
        for _ in range(samples_per_byte):
            audio_samples.append(val)
            
    total_samples = len(audio_samples)
    data_size = total_samples * 2
    header = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16, b'data', data_size)
    
    pcm_data = bytearray(header)
    for sample in audio_samples:
        pcm_data.extend(struct.pack('<h', sample))
        
    return bytes(pcm_data)

def decode_audio_digital(wav_bytes: bytes) -> str:
    """Dijital ses verisinden orijinal metni %100 hatasız çözer"""
    if len(wav_bytes) < 44:
        return "Geçersiz ses dosyası!"
    
    samples_per_byte = 50
    raw_audio = wav_bytes[44:]
    samples = []
    for i in range(0, len(raw_audio) - 1, 2):
        val = struct.unpack('<h', raw_audio[i:i+2])[0]
        samples.append(val)
        
    recovered_bytes = bytearray()
    total_bytes = len(samples) // samples_per_byte
    
    for b_idx in range(total_bytes):
        chunk = samples[b_idx * samples_per_byte : (b_idx + 1) * samples_per_byte]
        avg_val = sum(chunk) // len(chunk)
        b_val = int((avg_val / 200) + 128)
        b_val = max(0, min(255, b_val))
        recovered_bytes.append(b_val)
        
    decrypted = process_bytes(bytes(recovered_bytes))
    try:
        return decrypted.decode('utf-8')
    except Exception:
        return "Şifre çözülemedi."

def gelismis_ebced_hesapla(metin: str):
    """Türkçe, Osmanlıca ve Arapça metinlerin Ebced skorunu hesaplar."""
    toplam = 0
    detaylar = []
    for harf in metin.strip().lower():
        if harf in EBCED_ARAPCA:
            deger = EBCED_ARAPCA[harf]
            toplam += deger
            detaylar.append(f"{harf}: {deger}")
        elif harf in EBCED_TURKCE:
            deger = EBCED_TURKCE[harf]
            toplam += deger
            detaylar.append(f"{harf.upper()}: {deger}")
    return toplam, detaylar

# ==========================================
# KÜKNER MARKALAMA & YAN MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px; border-bottom: 2px solid #00d2ff; margin-bottom: 20px;">
            <h1 style="color: #00d2ff; margin:0; font-size: 28px; font-weight: 900; letter-spacing: 3px;">KÜKNER</h1>
            <p style="color: #8b949e; margin:0; font-size: 11px; letter-spacing: 1px;">SECURITY & CRYPTO STUDIO</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🦅 Sistem Özellikleri")
    st.info("KÜKNER Core: Aktif")
    st.caption(f"Matematiksel Sabit: {FACTOR:.8f}")
    st.divider()
    st.caption("© 2026 KÜKNER Teknolojileri. Tüm hakları saklıdır.")

# ==========================================
# ANA BAŞLIK
# ==========================================
st.title("🦅 KÜKNER Crypto Studio Pro")
st.caption("Gelişmiş Ses Steganografisi, Kriptografi ve Ebced Analiz Platformu")

# Sekmeler
tabs = st.tabs([
    "🎙️ Ses Laboratuvarı (Üretici & Çözücü)", 
    "📝 Metin Şifreleme / Çözme", 
    "🕌 Ebced Analizi (TR / AR / OSM)", 
    "📁 Dosya Kılavuzu & Kilitleme"
])

# ---------------------------------------------------------
# TAB 1: TEK SAYFADA SES LABORATUVARI (ÜRETİCİ & ÇÖZÜCÜ)
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("🎙️ Ses Sinyali İşleme Laboratuvarı")
    st.write("Metinlerinizi ses dalgalarına dönüştürün veya indirdiğiniz ses dosyalarından gizli metni geri okuyun.")
    
    col_gen, col_dec = st.columns(2)
    
    with col_gen:
        st.markdown("#### 1️⃣ Ses Sinyali Üret & İndir")
        audio_in = st.text_area("Sese dönüştürülecek metin:", value="KÜKNER Gizli Mesaj 2026", key="a_in", height=120)
        
        if st.button("🔊 Ses Dosyası Oluştur", key="b_gen"):
            if audio_in.strip():
                wav_data = generate_audio_digital(audio_in)
                st.success("Ses Sinyali Başarıyla Üretildi!")
                st.audio(wav_data, format="audio/wav")
                st.download_button(
                    label="📥 Ses Dosyasını İndir (.wav)",
                    data=wav_data,
                    file_name="kukner_secret_audio.wav",
                    mime="audio/wav",
                    key="d_wav"
                )
            else:
                st.warning("Lütfen bir metin girin.")

    with col_dec:
        st.markdown("#### 2️⃣ Ses Dosyasından Metin Çöz")
        uploaded_sound = st.file_uploader(".wav Formatında Ses Dosyası Yükleyin:", type=["wav"], key="s_up")
        
        if st.button("🔍 Sesi Analiz Et ve Metne Çevir", key="b_dec"):
            if uploaded_sound is not None:
                sound_bytes = uploaded_sound.read()
                result_text = decode_audio_digital(sound_bytes)
                st.success("Analiz Tamamlandı!")
                st.markdown("**Çözülen Orijinal Metin:**")
                st.code(result_text, language="text")
            else:
                st.warning("Lütfen önce bir .wav dosyası yükleyin.")

# ---------------------------------------------------------
# TAB 2: METİN ŞİFRELEME (HATASIZ HALE GETİRİLDİ)
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("📝 KÜKNER Simetrik Metin Şifreleme Engine")
    
    m1, m2 = st.columns(2)
    with m1:
        mode_txt = st.radio("İşlem Türü Seçin", ["Metni Şifrele", "Şifreli Metni Çöz"], key="m_txt")
        txt_input = st.text_area("Metin Girdisi:", height=150, placeholder="Metninizi yazın...", key="t_in")
        btn_txt = st.button("İşlemi Başlat", key="b_txt")
        
    with m2:
        if btn_txt and txt_input and txt_input.strip():
            try:
                if mode_txt == "Metni Şifrele":
                    raw_bytes = txt_input.encode('utf-8')
                    encrypted_bytes = process_bytes(raw_bytes)
                    result_out = base64.b64encode(encrypted_bytes).decode('utf-8')
                    st.success("Şifrelenmiş Metin (Base64):")
                    st.code(result_out, language="text")
                else:
                    decoded_base64 = base64.b64decode(txt_input.strip().encode('utf-8'))
                    decrypted_bytes = process_bytes(decoded_base64)
                    result_out = decrypted_bytes.decode('utf-8')
                    st.success("Çözülen Orijinal Metin:")
                    st.write(result_out)
            except Exception as ex:
                st.error("Hata: Girdi formatı çözülemedi! Lütfen şifre çözerken geçerli bir Base64 dizgisi girin.")

# ---------------------------------------------------------
# TAB 3: EBCED ANALİZİ
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("🕌 Çok Dilli Ebced Değeri Hesaplayıcı")
    st.write("Türkçe (Latin), Osmanlıca ve Arapça kelimelerin Ebced skorunu otomatik hesaplar.")
    
    ebced_in = st.text_area("Kelime veya cümle girin:", value="Kükner", key="e_in")
    if st.button("🧮 Ebced Skorunu Hesapla", key="b_ebced"):
        if ebced_in.strip():
            toplam_skor, harf_detaylari = gelismis_ebced_hesapla(ebced_in)
            st.success(f"Girdi: '{ebced_in}' | Toplam Ebced Değeri: {toplam_skor}")
            if harf_detaylari:
                st.markdown("**Harf Detayları:**")
                st.code(" + ".join(harf_detaylari) + f" = {toplam_skor}", language="text")
        else:
            st.warning("Lütfen bir kelime girin.")

# ---------------------------------------------------------
# TAB 4: DOSYA KİLİTLEME
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("📁 Dosya Şifreleme ve Kilit")
    st.write("Her türlü dosyayı (.pdf, .png, .docx vb.) KÜKNER sabitiyle güvenle kilitleyin veya açın.")
    
    uploaded_f = st.file_uploader("Dosya Seçin:", key="f_up")
    if st.button("Dosyayı İşle (Kilitle / Çöz)", key="b_f") and uploaded_f:
        file_bytes = uploaded_f.read()
        processed_file = process_bytes(file_bytes)
        st.success("Dosya İşleme Başarılı!")
        st.download_button(
            label="📥 İşlenmiş Dosyayı İndir", 
            data=processed_file, 
            file_name=f"kukner_locked_{uploaded_f.name}"
        )
