import streamlit as st
import base64
import hashlib
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

def generate_audio(data_bytes: bytes):
    """Metin verisini frekans tabanlı karmaşık ses sinyaline dönüştürür"""
    if not data_bytes: return b"", []
    sample_rate = 8000
    duration_per_byte = 0.05
    num_samples = int(sample_rate * duration_per_byte)
    
    audio_samples = []
    plot_data = []
    
    for i, b in enumerate(data_bytes[:100]):
        freq = 300 + (b * FACTOR)
        for s in range(num_samples):
            t = s / sample_rate
            val = math.sin(2 * math.pi * freq * t)
            audio_samples.append(int(val * 32767))
            if i < 4: plot_data.append(val)
                
    total_samples = len(audio_samples)
    data_size = total_samples * 2
    header = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16, b'data', data_size)
    
    pcm_data = bytearray(header)
    for sample in audio_samples:
        pcm_data.extend(struct.pack('<h', sample))
    return bytes(pcm_data), plot_data

def decode_audio_to_text(wav_bytes: bytes) -> str:
    """Yüklenen karmaşık ses dosyasını analiz eder ve içindeki gizli yazıyı çözer"""
    if len(wav_bytes) < 44:
        return "Geçersiz veya bozuk ses dosyası!"
    
    sample_rate = 8000
    duration_per_byte = 0.05
    num_samples_per_byte = int(sample_rate * duration_per_byte)
    
    # WAV Başlığını atla, sadece ses verisini oku
    raw_audio = wav_bytes[44:]
    samples = []
    for i in range(0, len(raw_audio) - 1, 2):
        val = struct.unpack('<h', raw_audio[i:i+2])[0]
        samples.append(val / 32767.0)
        
    recovered_bytes = bytearray()
    total_chunks = len(samples) // num_samples_per_byte
    
    for b_idx in range(total_chunks):
        chunk = samples[b_idx * num_samples_per_byte : (b_idx + 1) * num_samples_per_byte]
        # Frekans tespiti (Zero-Crossing Rate)
        crossings = sum(1 for i in range(len(chunk)-1) if (chunk[i] >= 0 and chunk[i+1] < 0) or (chunk[i] < 0 and chunk[i+1] >= 0))
        freq_est = (crossings * sample_rate) / (2 * len(chunk))
        
        # Frekanstan orijinal byte değerini geri hesapla
        b_val = int(round((freq_est - 300) / FACTOR))
        b_val = max(0, min(255, b_val))
        recovered_bytes.append(b_val)
        
    decrypted = process_bytes(bytes(recovered_bytes))
    try:
        return decrypted.decode('utf-8')
    except:
        return "Ses çözüldü ancak metin okunamadı."

# Başlık
st.title("🎙️ MathCrypt Audio Studio Pro")
st.caption("100 / 3⁵ × 19 Sabiti Tabanlı Ses Sentezleme ve Yazıya Dönüştürme Sistemi")

tabs = st.tabs(["🔊 Ses Üretici (Metin ➔ Ses)", "🎙️ Ses Çözücü (Ses ➔ Metin)", "📝 Metin Şifreleme", "🎨 Renk Paleti", "📁 Dosya Kilitleme"])

# ---------------------------------------------------------
# TAB 1: METİNDEN SES ÜRETME
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("🔊 Metni Gizli Ses Sinyaline Çevir")
    st.write("Yazdığınız kelimeler matematiksel sabit ile karmaşık frekans seslerine dönüştürülür.")
    audio_in = st.text_area("Sese dönüştürülecek kelimeleri yazın:", value="Gizli Mesaj 2026", key="a_in")
    if st.button("🔊 Ses Sinyali Üret", key="b_gen_aud"):
        if audio_in.strip():
            enc_bytes = process_bytes(audio_in.encode('utf-8'))
            wav_data, plot_vals = generate_audio(enc_bytes)
            st.success("Ses Sinyali Başarıyla Oluşturuldu!")
            
            st.audio(wav_data, format="audio/wav")
            
            st.download_button(
                label="📥 Ses Dosyasını İndir (.wav)",
                data=wav_data,
                file_name="secret_sound.wav",
                mime="audio/wav"
            )
            st.markdown("**📊 Ses Dalga Grafiği:**")
            st.line_chart(plot_vals[:200])

# ---------------------------------------------------------
# TAB 2: SESTENT METİN ÇÖZME (YENİ ÖZELLİK)
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("🎙️ Karmaşık Ses Dosyasını Yazıya Dönüştür")
    st.write("Bu uygulamada oluşturulan `.wav` ses dosyasını yükleyin, içindeki gizli metni anında okuyun.")
    
    uploaded_sound = st.file_uploader("Çözülecek Ses Dosyasını Seçin (.wav)", type=["wav"], key="sound_up")
    btn_decode_sound = st.button("🔍 Sesi Analiz Et ve Metne Çevir", key="b_dec_sound")
    
    if btn_decode_sound:
        if uploaded_sound is not None:
            try:
                sound_bytes = uploaded_sound.read()
                revealed_text = decode_audio_to_text(sound_bytes)
                
                st.success("🎉 Ses Başarıyla Çözüldü!")
                st.markdown("**Çözülen Yazılı Metin:**")
                st.code(revealed_text, language="text")
            except Exception as ex:
                st.error(f"Ses analiz edilirken bir hata oluştu: {str(ex)}")
        else:
            st.warning("Lütfen önce çözülecek bir .wav ses dosyası yükleyin.")

# ---------------------------------------------------------
# TAB 3: METİN ŞİFRELEME
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("📝 Metin Şifreleme")
    c1, c2 = st.columns(2)
    with c1:
        txt_in = st.text_area("Şifrelenecek Metin:", key="t_in")
        btn_txt = st.button("Şifrele", key="b_txt")
    with c2:
        if btn_txt and txt_in.strip():
            processed = process_bytes(txt_in.encode('utf-8'))
            out_str = base64.b64encode(processed).decode('utf-8')
            st.success("Şifrelenmiş Metin:")
            st.code(out_str, language="text")

# ---------------------------------------------------------
# TAB 4: RENK PALETİ
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("🎨 Metni Renklere Gizle")
    color_in = st.text_input("Renklere çevrilecek metin:", key="c_in")
    if st.button("Renklere Çevir", key="b_col") and color_in.strip():
        enc = process_bytes(color_in.encode('utf-8'))
        colors = []
        for i in range(0, len(enc), 3):
            chunk = enc[i:i+3] + b'\x00' * (3 - len(enc[i:i+3]))
            r, g, b_val = int((chunk[0]*FACTOR)%256), int((chunk[1]*FACTOR)%256), int((chunk[2]*FACTOR)%256)
            colors.append(f"#{r:02x}{g:02x}{b_val:02x}")
        
        cols = st.columns(min(len(colors), 8))
        for idx, hx in enumerate(colors[:16]):
            with cols[idx % 8]:
                st.markdown(f'<div style="background-color:{hx}; height:50px; border-radius:5px;"></div>', unsafe_allow_html=True)
                st.caption(hx)

# ---------------------------------------------------------
# TAB 5: DOSYA KİLİTLEME
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("📁 Dosya Kilitleme")
    uploaded = st.file_uploader("Dosya Seç", key="f_up")
    if st.button("Kilitle/Çöz", key="b_f") and uploaded:
        processed = process_bytes(uploaded.read())
        st.download_button("İşlenmiş Dosyayı İndir", processed, file_name=f"locked_{uploaded.name}")
