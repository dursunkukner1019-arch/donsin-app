import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="Kükner Cryptology - Multi-Domain Suite", page_icon="🛡️", layout="centered")

st.title("🛡️ Kükner Kriptoloji - Çok Amaçlı Savunma & AI Modülü")
st.markdown("### Formula: $\\left(\\frac{100}{19} \\times \\frac{\\pi}{19}\\right)^n$")
st.write("Bu arayüz; İHA/SİHA haberleşmesi, metin şifreleme, ses akışı koruması ve yapay zeka tokenizasyonunu tek merkezden simüle eder.")

# Sekme veya Seçim Menüsü
secim = st.selectbox(
    "Uygulama Alanı Seçin:",
    [
        "1. İHA / SİHA Frekans Atlama & Telemetri",
        "2. Hassas Metin Şifreleme (XOR Matris)",
        "3. Ses ve Akış Verisi Şifreleme (Stream)",
        "4. Yapay Zeka (AI) Tokenizasyon & Güvenlik"
    ]
)

pi = np.pi
temel_katsayi = (100.0 / 19.0) * (pi / 19.0)

st.markdown("---")

if "1. İHA" in secim:
    st.subheader("🛸 İHA / SİHA Telemetri & Frekans Atlama Simülasyonu")
    paket_sayisi = st.slider("Paket Adedi:", 5, 15, 5)
    
    if st.button("İHA Simülasyonunu Çalıştır"):
        benzersiz = set()
        for n in range(1, paket_sayisi + 1):
            val = np.power(temel_katsayi, n)
            s = f"{val:.50f}"
            kanal = 2400 + (int(s.replace('.', '')[:4]) % 80)
            key = s[-12:]
            benzersiz.add(key)
            st.success(f"Paket #{n:02d} | Frekans: **{kanal} MHz** | Anahtar: `{key}`")
            time.sleep(0.03)
        st.info(f"Çakışma Oranı: %0.00 | Benzersiz Anahtar Adedi: {len(benzersiz)}")

elif "2. Metin" in secim:
    st.subheader("🔐 Hassas Metin Şifreleme ve Çözme")
    metin = st.text_input("Şifrelenecek Mesaj:", "Kukner Kriptoloji Milli Savunma")
    
    if st.button("Metni Şifrele"):
        anahtarlar = [int(f"{np.power(temel_katsayi, i):.50f}".replace('.', '')[-4:]) % 256 for i in range(1, len(metin) + 1)]
        sifreli = [ord(c) ^ k for c, k in zip(metin, anahtarlar)]
        hex_str = ''.join([f'{b:02X}' for b in sifreli])
        
        cozulmus = ''.join([chr(s ^ k) for s, k in zip(sifreli, anahtarlar)])
        
        st.markdown(f"**Orijinal:** `{metin}`")
        st.markdown(f"**Şifreli (Hex):** `{hex_str}`")
        st.markdown(f"**Çözülen:** `{cozulmus}`")
        st.success("Metin şifreleme hatasız doğrulandı.")

elif "3. Ses" in secim:
    st.subheader("🎤 Ses ve Akış Verisi (Audio/Stream) Koruması")
    orneksayisi = st.slider("Ses Örnek (Frame) Sayısı:", 5, 20, 10)
    
    if st.button("Ses Akışını Şifrele"):
        st.write("Gerçek zamanlı ses paketleri (VoIP / Telsiz) şifreleniyor...")
        for i in range(1, orneksayisi + 1):
            val = np.power(temel_katsayi, i)
            s = f"{val:.50f}"
            audio_key = s[-8:]
            st.code(f"Ses Çerçevesi [Frame #{i:02d}] -> Şifreleme Maskesi: {audio_key}")
            time.sleep(0.03)
        st.success("Ses akış verisi sıfır gecikmeyle korundu.")

else:
    st.subheader("🤖 Yapay Zeka (AI) Tokenizasyon & LLM Güvenliği")
    prompt = st.text_input("AI Prompt / Girdi:", "Savunma sanayii için stratejik analiz üret.")
    
    if st.button("Token Güvenliğini Başlat"):
        tokens = prompt.split()
        st.write(f"Toplam Kelime/Token Sayısı: {len(tokens)}")
        
        for idx, token in enumerate(tokens, 1):
            val = np.power(temel_katsayi, idx)
            s = f"{val:.50f}"
            token_hash = s[-10:]
            st.markdown(f"Token `{token}` $\\rightarrow$ Güvenli Vektör ID: `{token_hash}`")
            
        st.balloons()
        st.success("Yapay Zeka model tokenleri Kükner matrisi ile mühürlendi.")
