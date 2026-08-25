import streamlit as st
import base64
import struct

# Sayfa Yapılandırması
st.set_page_config(page_title="MathCrypt Voice Studio", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #00d2ff; color: #000; font-weight: bold; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #0087ff; color: #fff; box-shadow: 0 0 10px #00d2ff; }
</style>
""", unsafe_allow_html=True)

# 100 / 3⁵ × 19 Matematiksel Sabiti
FACTOR = (100 / (3 ** 5)) * 19  # ≈ 7.818930041152263

# 1. Standart Arapça/Osmanlıca Ebced Tablosu
EBCED_ARAPCA = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ء': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 
    'ح': 8, 'ط': 9, 'ي': 10, 'ى': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 
    'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 
    'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000, 'پ': 2, 'چ': 3, 'ژ': 7, 'گ': 20
}

# 2. Türkçe/Latin Harflerin Osmanlıca Phonetic Ebced Haritası
EBCED_TURKCE = {
    'a': 1, 'b': 2, 'c': 3, 'ç': 3, 'd': 4, 'e': 5, 'f': 80, 'g': 20, 'ğ': 1000,
    'h': 8, 'ı': 10, 'i': 10, 'j': 7, 'k': 20, 'l': 30, 'm': 40, 'n': 50, 'o': 6,
    'ö': 6, 'p': 2, 'r': 200, 's': 60, 'ş': 300, 't': 400, 'u': 6, 'ü': 6, 'v': 6,
    'y': 10, 'z': 7
}

def gelismis_ebced_hesapla(metin: str):
    """Türkçe, Osmanlıca ve Arapça metinleri ayırt ederek Ebced değerini hesaplar."""
    toplam = 0
    detaylar = []
    
    metin_lower = metin.strip().lower()
    
    for harf in metin_lower:
        # Önce Arapça/Osmanlıca karakter kontrolü
        if harf in EBCED_ARAPCA:
            deger = EBCED_ARAPCA[harf]
            toplam += deger
            detaylar.append(f"{harf}: {deger}")
        # Türkçe / Latin karakter kontrolü
        elif harf in EBCED_TURKCE:
            deger = EBCED_TURKCE[harf]
            toplam += deger
            detaylar.append(f"{harf.upper()}: {deger}")
            
    return toplam, detaylar

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

# Başlık
st.title("🎙️ MathCrypt Audio Studio Pro")
st.caption("Kayıpsız Ses Şifreleme, Çözme ve Çok Dilli Ebced Analiz Sistemi")

tabs = st.tabs(["🔊 Ses Üretici & İndir", "🎙️ Ses Çözücü", "🕌 Ebced Hesabı (TR/AR/OSM)", "📝 Metin Şifreleme", "📁 Dosya Kilitleme"])

# ---------------------------------------------------------
# TAB 1: SES ÜRET VE İNDİR
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("🔊 Metni Sese Çevir ve İndir")
    audio_in = st.text_area("Sese dönüştürülecek metin:", value="Gizli Mesaj 2026", key="a_in")
    
    if st.button("🔊 Ses Sinyali Üret ve İndirme Bağlantısı Hazırla", key="b_gen"):
        if audio_in.strip():
            wav_data = generate_audio_digital(audio_in)
            st.success("Ses Sinyali Hazır!")
            st.audio(wav_data, format="audio/wav")
            st.download_button(
                label="📥 Ses Dosyasını İndir (.wav)",
                data=wav_data,
                file_name="secret_audio.wav",
                mime="audio/wav",
                key="d_wav"
            )

# ---------------------------------------------------------
# TAB 2: SES ÇÖZÜCÜ
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("🎙️ İndirilen Ses Dosyasını Yazıya Çevir")
    uploaded_sound = st.file_uploader("İndirdiğiniz .wav ses dosyasını yükleyin:", type=["wav"], key="s_up")
    
    if st.button("🔍 Sesi Metne Dönüştür", key="b_dec"):
        if uploaded_sound is not None:
            sound_bytes = uploaded_sound.read()
            result_text = decode_audio_digital(sound_bytes)
            st.success("Çözme İşlemi Tamamlandı!")
            st.markdown("**Çözülen Metin:**")
            st.code(result_text, language="text")
        else:
            st.warning("Lütfen bir .wav dosyası yükleyin.")

# ---------------------------------------------------------
# TAB 3: GELİŞMİŞ EBCED HESABI (TÜRKÇE / ARAPÇA / OSMANLICA)
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("🕌 Çok Dilli Ebced Değeri Hesaplayıcı")
    st.write("Türkçe (Latin), Osmanlıca veya Arapça fark etmeksizin girilen tüm kelimelerin Ebced skorunu anında hesaplar.")
    
    ebced_in = st.text_area("Ebced hesabı yapılacak kelime veya cümleyi girin:", value="Ahmet", key="e_in")
    
    if st.button("🧮 Ebced Değerini Hesapla", key="b_ebced"):
        if ebced_in.strip():
            toplam_skor, harf_detaylari = gelismis_ebced_hesapla(ebced_in)
            
            st.success(f"Girdi: '{ebced_in}' | Toplam Ebced Değeri: {toplam_skor}")
            
            if harf_detaylari:
                st.markdown("**Harf Harf Ebced Dökümü:**")
                st.code(" + ".join(harf_detaylari) + f" = {toplam_skor}", language="text")
            else:
                st.warning("Hesaplanabilir geçerli bir karakter bulunamadı.")
        else:
            st.warning("Lütfen bir kelime girin.")

# ---------------------------------------------------------
# TAB 4: METİN ŞİFRELEME
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("📝 Standart Metin Şifreleme")
    txt_in = st.text_area("Metin:", key="t_in")
    if st.button("Şifrele", key="b_txt") and txt_in.strip():
        processed = process_bytes(txt_in.encode('utf-8'))
        st.code(base64.b64encode(processed).decode('utf-8'), language="text")

# ---------------------------------------------------------
# TAB 5: DOSYA KİLİTLEME
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("📁 Dosya Kilitleme")
    uploaded = st.file_uploader("Dosya Seç", key="f_up")
    if st.button("Kilitle/Çöz", key="b_f") and uploaded:
        processed = process_bytes(uploaded.read())
        st.download_button("İşlenmiş Dosyayı İndir", processed, file_name=f"locked_{uploaded.name}")
