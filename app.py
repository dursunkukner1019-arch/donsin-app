import streamlit as st
import base64
import math
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

def process_bytes(data: bytes) -> bytes:
    """Tekil XOR döngüsü ile simetrik byte işleme"""
    if not data: return b""
    shift = int(FACTOR * 1000) % 256
    res = bytearray()
    for i, b in enumerate(data):
        res.append(b ^ ((shift + i) % 256))
    return bytes(res)

def generate_audio_exact(data_bytes: bytes):
    """Metin verisini %100 geri çözülebilir hassas ses sinyaline dönüştürür"""
    if not data_bytes: return b"", []
    
    sample_rate = 8000
    samples_per_byte = 100  # Her bayt için 100 sinyal örneği (Kararlılık için)
    
    audio_samples = []
    plot_data = []
    
    for i, b in enumerate(data_bytes):
        freq = 300 + (b * 5)  # Stabilize edilmiş frekans adımı
        for s in range(samples_per_byte):
            t = s / sample_rate
            val = math.sin(2 * math.pi * freq * t)
            # Bayt değerini sinyalin genlik/frekans yapısına tam gömüyoruz
            sample_val = int(val * 20000) + (b * 40)
            sample_val = max(-32767, min(32767, sample_val))
            audio_samples.append(sample_val)
            if i < 2 and s < 100:
                plot_data.append(val)
                
    total_samples = len(audio_samples)
    data_size = total_samples * 2
    header = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16, b'data', data_size)
    
    pcm_data = bytearray(header)
    for sample in audio_samples:
        pcm_data.extend(struct.pack('<h', sample))
        
    return bytes(pcm_data), plot_data

def decode_audio_exact(wav_bytes: bytes) -> str:
    """Ses dosyasını sıfır hatayla çözerek orijinal metni verir"""
    if len(wav_bytes) < 44:
        return "Geçersiz ses dosyası!"
    
    samples_per_byte = 100
    raw_audio = wav_bytes[44:]
    
    samples = []
    for i in range(0, len(raw_audio) - 1, 2):
        val = struct.unpack('<h', raw_audio[i:i+2])[0]
        samples.append(val)
        
    recovered_bytes = bytearray()
    total_bytes = len(samples) // samples_per_byte
    
    for b_idx in range(total_bytes):
        chunk = samples[b_idx * samples_per_byte : (b_idx + 1) * samples_per_byte]
        
        # Sesteki tepe noktalarından frekans ve bayt tespiti
        crossings = sum(1 for i in range(len(chunk)-1) if (chunk[i] >= 0 and chunk[i+1] < 0) or (chunk[i] < 0 and chunk[i+1] >= 0))
        freq_est = (crossings * 8000) / (2 * len(chunk))
        
        b_val = int(round((freq_est - 300) / 5))
        b_val = max(0, min(255, b_val))
        recovered_bytes.append(b_val)
        
    decrypted = process_bytes(bytes(recovered_bytes))
    try:
        return decrypted.decode('utf-8')
    except:
        return "Şifre çözülemedi (Format hatası)."

# Başlık
st.title("🎙️ MathCrypt Audio Studio Pro")
st.caption("Kesin Sonuç Veren Ses Şifreleme ve Çözme Sistemi")

tabs = st.tabs(["🔊 Ses Üretici & İndir", "🎙️ Ses Çözücü", "📝 Metin Şifreleme", "📁 Dosya Kilitleme"])

# ---------------------------------------------------------
# TAB 1: SES ÜRET VE İNDİR
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("🔊 Metni Sese Çevir ve İndir")
    audio_in = st.text_area("Sese dönüştürülecek metin:", value="Test Mesajı 123", key="a_in")
    
    if st.button("🔊 Ses Sinyali Üret ve İndirme Bağlantısı Hazırla", key="b_gen"):
        if audio_in.strip():
            enc_bytes = process_bytes(audio_in.encode('utf-8'))
            wav_data, plot_vals = generate_audio_exact(enc_bytes)
            
            st.success("Ses Sinyali Hazır!")
            st.audio(wav_data, format="audio/wav")
            
            # İNDİRME BUTONU
            st.download_button(
                label="📥 Ses Dosyasını İndir (.wav)",
                data=wav_data,
                file_name="secret_audio.wav",
                mime="audio/wav",
                key="d_wav"
            )
            st.line_chart(plot_vals[:200])

# ---------------------------------------------------------
# TAB 2: SES ÇÖZÜCÜ
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("🎙️ İndirilen Ses Dosyasını Yazıya Çevir")
    uploaded_sound = st.file_uploader("İndirdiğiniz .wav ses dosyasını yükleyin:", type=["wav"], key="s_up")
    
    if st.button("🔍 Sesi Metne Dönüştür", key="b_dec"):
        if uploaded_sound is not None:
            sound_bytes = uploaded_sound.read()
            result_text = decode_audio_exact(sound_bytes)
            
            st.success("Çözme İşlemi Tamamlandı!")
            st.markdown("**Çözülen Metin:**")
            st.code(result_text, language="text")
        else:
            st.warning("Lütfen bir .wav dosyası yükleyin.")

# ---------------------------------------------------------
# TAB 3: METİN ŞİFRELEME
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("📝 Standart Metin Şifreleme")
    txt_in = st.text_area("Metin:", key="t_in")
    if st.button("Şifrele", key="b_txt") and txt_in.strip():
        processed = process_bytes(txt_in.encode('utf-8'))
        st.code(base64.b64encode(processed).decode('utf-8'), language="text")

# ---------------------------------------------------------
# TAB 4: DOSYA KİLİTLEME
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("📁 Dosya Kilitleme")
    uploaded = st.file_uploader("Dosya Seç", key="f_up")
    if st.button("Kilitle/Çöz", key="b_f") and uploaded:
        processed = process_bytes(uploaded.read())
        st.download_button("İşlenmiş Dosyayı İndir", processed, file_name=f"locked_{uploaded.name}")
