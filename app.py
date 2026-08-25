import streamlit as st
import base64
import math
import struct

# Sayfa Yapılandırması
st.set_page_config(page_title="MathSignal Studio", page_icon="📡", layout="wide")

# 100 / 3⁵ × 19 Matematiksel Sabiti (Sabit Faktör)
FACTOR = (100 / (3 ** 5)) * 19  # ≈ 7.818930041152263

def process_data(data: bytes) -> bytes:
    """Verilen byte verisini matematiksel sabit ile XOR döngüsüne sokar."""
    if not data:
        return b""
    shift = int(FACTOR * 1000) % 256
    res = bytearray()
    for i, b in enumerate(data):
        res.append(b ^ ((shift + i) % 256))
    return bytes(res)

def generate_wave(data_bytes: bytes):
    """Bayt verisini hatasız WAV ses sinyaline ve grafik verisine dönüştürür."""
    if not data_bytes:
        return b"", []
        
    sample_rate = 8000
    duration_per_byte = 0.05
    num_samples_per_byte = int(sample_rate * duration_per_byte)
    
    audio_samples = []
    plot_data = []
    
    for i, b in enumerate(data_bytes[:100]):
        freq = 300 + (b * FACTOR)
        for s in range(num_samples_per_byte):
            t = s / sample_rate
            val = math.sin(2 * math.pi * freq * t)
            audio_samples.append(int(val * 32767))
            if i < 5:
                plot_data.append(val)
                
    num_samples = len(audio_samples)
    data_size = num_samples * 2
    header = struct.pack('<4sI4s4sIHHIIHH4sI', 
        b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16, 1, 1, sample_rate, 
        sample_rate * 2, 2, 16, b'data', data_size)
    
    pcm_data = bytearray(header)
    for sample in audio_samples:
        pcm_data.extend(struct.pack('<h', sample))
        
    return bytes(pcm_data), plot_data

# Arayüz Başlığı
st.title("📡 MathSignal Studio")
st.caption("100 / 3⁵ × 19 Sabiti Tabanlı Güvenli İşlem Platformu")

tab_signal, tab_text, tab_file = st.tabs(["📡 Sinyal & Ses", "📝 Metin İşleme", "📁 Dosya İşleme"])

# ==========================================
# SEKME 1: SİNYAL VE SES ANALİZİ
# ==========================================
with tab_signal:
    st.subheader("🔊 Sinyal Modülasyonu ve Ses Üretici")
    
    col_sig1, col_sig2 = st.columns(2)
    
    with col_sig1:
        sig_input = st.text_area("Sinyale Dönüştürülecek Metin", value="SOS 123", height=120, key="sig_in")
        btn_sig = st.button("📡 Sinyal Üret", key="b_sig")
        
    with col_sig2:
        if btn_sig:
            if sig_input and sig_input.strip():
                try:
                    enc_bytes = process_data(sig_input.encode('utf-8'))
                    wav_bytes, plot_values = generate_wave(enc_bytes)
                    
                    st.success("Sinyal Başarıyla Oluşturuldu!")
                    st.audio(wav_bytes, format="audio/wav")
                    
                    st.markdown("**📊 Şifreli Sinyal Dalga Formu (Waveform):**")
                    st.line_chart(plot_values[:200])
                except Exception as ex:
                    st.error(f"İşlem sırasında bir hata oluştu: {str(ex)}")
            else:
                st.warning("Lütfen sinyale dönüştürmek için bir metin girin.")

# ==========================================
# SEKME 2: METİN İŞLEMLERİ
# ==========================================
with tab_text:
    st.subheader("Metin Modülü")
    col1, col2 = st.columns(2)
    
    with col1:
        mode_text = st.radio("İşlem Türü", ["Şifrele", "Şifre Çöz"], key="m_text")
        txt_input = st.text_area("Metin Girdisi", height=150, key="txt_in")
        btn_txt = st.button("Metni İşle", key="b_txt")
        
    with col2:
        if btn_txt:
            if txt_input and txt_input.strip():
                try:
                    if mode_text == "Şifrele":
                        raw = txt_input.encode('utf-8')
                        enc = process_data(raw)
                        out = base64.b64encode(enc).decode('utf-8')
                        st.success("Metin Şifrelendi:")
                        st.code(out, language="text")
                    else:
                        raw = base64.b64decode(txt_input.strip().encode('utf-8'))
                        dec = process_data(raw)
                        out = dec.decode('utf-8')
                        st.success("Şifre Çözüldü:")
                        st.write(out)
                except Exception:
                    st.error("Şifre çözülemedi! Girdinin geçerli bir Base64 formatında olduğundan emin olun.")
            else:
                st.warning("Lütfen işlem yapılacak metni girin.")

# ==========================================
# SEKME 3: DOSYA İŞLEMLERİ
# ==========================================
with tab_file:
    st.subheader("Dosya Modülü")
    col1, col2 = st.columns(2)
    
    with col1:
        file_obj = st.file_uploader("Bir Dosya Seçin", key="fl_up")
        btn_file = st.button("Dosyayı İşle", key="b_file")
        
    with col2:
        if btn_file:
            if file_obj is not None:
                try:
                    content = file_obj.read()
                    processed = process_data(content)
                    
                    st.success("Dosya İşlendi!")
                    st.download_button(
                        label="İşlenmiş Dosyayı İndir",
                        data=processed,
                        file_name=f"processed_{file_obj.name}",
                        mime="application/octet-stream"
                    )
                except Exception as ex:
                    st.error(f"Dosya okuma/yazma hatası: {str(ex)}")
            else:
                st.warning("Lütfen önce bir dosya yükleyin.")
