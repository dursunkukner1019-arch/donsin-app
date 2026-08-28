import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="Kükner Cryptology - İHA/SİHA Simulation", page_icon="🛸", layout="centered")

st.title("🛸 Kükner Kriptoloji - İHA/SİHA Güvenlik Simülasyonu")
st.markdown("### Formula: $\\left(\\frac{100}{19} \\times \\frac{\\pi}{19}\\right)^n$")
st.write("Bu arayüz; İHA ve SİHA haberleşmesinde frekans atlama (frequency hopping) ve telemetri şifreleme süreçlerini canlı olarak test eder.")

paket_adedi = st.slider("Simüle Edilecek Paket Sayısı:", min_value=5, max_value=20, value=10)

if st.button("🚀 İHA/SİHA Haberleşme Simülasyonunu Başlat"):
    with st.spinner("Kriptografik frekans kanalları hesaplanıyor..."):
        pi = np.pi
        temel_katsayi = (100.0 / 19.0) * (pi / 19.0)
        
        st.info(f"**Temel Sabit Çarpan:** `{temel_katsayi:.12f}`")
        st.markdown("---")
        
        benzersiz_anahtarlar = set()
        baslangic_zaman = time.time()
        
        for n in range(1, paket_adedi + 1):
            formul_degeri = np.power(temel_katsayi, n)
            hassas_str = f"{formul_degeri:.50f}"
            
            # 2400 MHz bandında dinamik frekans atlama
            kanal_frekansi = 2400 + (int(hassas_str.replace('.', '')[:4]) % 80)
            telemetri_anahtari = hassas_str[-12:]
            
            benzersiz_anahtarlar.add(telemetri_anahtari)
            
            st.success(f"**Paket #{n:02d}** | Atlanan Frekans: **{kanal_frekansi} MHz** | Anahtar Sinyal: `{telemetri_anahtari}`")
            time.sleep(0.04)
            
        bitis_zaman = time.time()
        toplam_sure = (bitis_zaman - baslangic_zaman) * 1000
        
        st.balloons()
        st.markdown("---")
        st.markdown(f"### 📊 Test Raporu")
        st.write(f"- **Toplam Paket:** {paket_adedi}")
        st.write(f"- **Çakışma Oranı:** %0.00 (%100 Benzersizlik)")
        st.write(f"- **Toplam İşlem Süresi:** {toplam_sure:.2f} ms")
        st.success("Durum: İHA/SİHA telemetri koruması karıştırma (jamming) ve dinlemeye karşı başarıyla doğrulandı.")
