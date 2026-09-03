import streamlit as st
import math
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

# Sayfa Yapılandırması
st.set_page_config(page_title="Kükner Kripto KDF Uygulaması", page_icon="🔒", layout="centered")

st.title("🔒 Kükner - Özel Matematiksel KDF & AES-256 Şifreleme")
st.write("Bu uygulama, özel seri ve modüler matematik formüllerini kullanarak güvenli 256-bit AES anahtarları türetir ve verilerinizi şifreler.")

# Yan Menü / Ayarlar
st.sidebar.header("Parametreler")
n_val = st.sidebar.number_input("Matematiksel Parametre (n)", min_value=1, max_value=100000, value=19)
terim_sayisi = st.sidebar.slider("Seri Terim Sayısı (Hassasiyet)", min_value=100, max_value=10000, value=1000, step=100)

# Özel KDF Fonksiyonu
def ozel_kdf_uret(n, terim_sayisi):
    toplam_deger = 0.0
    pi = math.pi
    for i in range(1, terim_sayisi + 1):
        terim = (99 / 19.0) * ((pi / 19.0) ** (i % 10)) * (n / 19.0)
        toplam_deger += terim / (i ** 1.1)
    
    ham_veri = ("KUKNER_WEB_APP::" + str(toplam_deger)).encode('utf-8')
    return hashlib.sha256(ham_veri).digest() # 32 Byte / 256-bit anahtar

# Sekmeler (Şifreleme / Çözme)
sekme1, sekme2 = st.tabs(["🔐 Şifreleme (Encrypt)", "🔓 Çözme (Decrypt)"])

with sekme1:
    st.subheader("Metin Şifreleme")
    gizli_mesaj = st.text_area("Şifrelenecek Gizli Metni Girin:", "Bu mesaj özel formülle korunmaktadır.")
    
    if st.button("Veriyi Şifrele"):
        if gizli_mesaj:
            anahtar = ozel_kdf_uret(n_val, terim_sayisi)
            iv = b'\x00' * 16  # Sabit Başlangıç Vektörü
            
            cipher = AES.new(anahtar, AES.MODE_CBC, iv)
            sifreli_veri = cipher.encrypt(pad(gizli_mesaj.encode('utf-8'), AES.block_size))
            
            st.success("Şifreleme Başarılı!")
            st.text_input("Üretilen 256-bit Anahtar (Hex):", value=anahtar.hex())
            st.text_area("Şifrelenmiş Veri (Hex - Kopyala ve Sakla):", value=sifreli_veri.hex())
        else:
            st.warning("Lütfen şifrelenecek bir metin yazın.")

with sekme2:
    st.subheader("Şifrelenmiş Veriyi Çözme")
    sifreli_hex = st.text_area("Şifrelenmiş Hex Verisini Buraya Yapıştırın:")
    
    if st.button("Veriyi Çöz"):
        if sifreli_hex:
            try:
                anahtar = ozel_kdf_uret(n_val, terim_sayisi)
                iv = b'\x00' * 16
                
                cipher = AES.new(anahtar, AES.MODE_CBC, iv)
                cozulen_veri = unpad(cipher.decrypt(bytes.fromhex(sifreli_hex)), AES.block_size).decode('utf-8')
                
                st.success("Çözme Başarılı!")
                st.text_area("Orijinal Metin:", value=cozulen_veri)
            except Exception as e:
                st.error(f"Çözme başarısız! Parametreler (n veya terim sayısı) yanlış olabilir ya da veri bozuk. Hata: {e}")
        else:
            st.warning("Lütfen çözülecek hex verisini girin.")
