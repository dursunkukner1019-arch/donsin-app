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

# Standart Ebced Değerleri Tablosu
EBCED_TABLOSU = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 
    'ح': 8, 'ط': 9, 'ي': 10, 'ى': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 
    'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 
    'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000, 'پ': 2, 'چ': 3, 'ژ': 7, 'گ': 20
}

def ebced_hesapla(metin: str):
    """Girilen metindeki Arapça/Osmanlıca harflerin Ebced değerini hesaplar."""
    toplam = 0
    detaylar = []
    for harf in metin:
        if harf in EBCED_TABLOSU:
            deger = EBCED_TABLOSU[harf]
            toplam += deger
            detaylar.append(f"{harf}: {deger}")
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
st.caption("Kayıpsız Ses Şifreleme, Çözme ve Ebced Analiz Sistemi")

tabs = st.tabs(["🔊 Ses Üretici & İndir", "🎙️ Ses Çözücü", "🕌 Ebced Hesabı", "📝 Metin Şifreleme", "📁 Dosya Kilitleme"])

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
# TAB 3: EBCED HESABI (YENİ MODÜL)
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("🕌 Ebced Değeri Hesaplayıcı")
    st.write("Arapça veya Osmanlıca metinlerin sayısal Ebced karşılığını hesaplar.")
    
    ebced_in = st.text_area("Ebced hesabı yapılacak Arapça/Osmanlıca metni girin:", value="علي", key="e_in")
    
    if st.button("🧮 Ebced Değerini Hesapla", key="b_ebced"):
        if ebced_in.strip():
            toplam_skor, harf_detaylari = ebced_hesapla(ebced_in)
            
            st.success(f"Toplam Ebced Değeri: {toplam_skor}")
            
            if harf_detaylari:
                st.markdown("**Harf Analizi:**")
                st.write(", ".join(harf_detaylari))
            else:
                st.warning("Metinde geçerli bir Arapça/Osmanlıca karakter bulunamadı.")
        else:
            st.warning("Lütfen bir metin girin.")

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
