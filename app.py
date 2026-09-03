import streamlit as st
import math
import hashlib
import base64

# Sayfa Yapılandırması
st.set_page_config(page_title="Kükner Kripto KDF", page_icon="🔒", layout="centered")

st.title("🔒 Kükner - Özel Matematiksel KDF & Güvenli Şifreleme")
st.write("Bu uygulama, matematiksel formülünüzle 256-bit anahtar üretir ve verilerinizi güvenle şifreler/çözer.")

# Yan Menü / Parametreler
st.sidebar.header("Parametreler")
n_val = st.sidebar.number_input("Matematiksel Parametre (n)", min_value=1.0, max_value=100000.0, value=19.0, key="sb_n")
terim_sayisi = st.sidebar.slider("Seri Terim Sayısı (Hassasiyet)", min_value=100, max_value=10000, value=1000, step=100, key="sb_terim")

# Özel KDF Fonksiyonu
def ozel_kdf_uret(n, terim_sayisi):
    toplam_deger = 0.0
    pi = math.pi
    for i in range(1, terim_sayisi + 1):
        terim = (99 / 19.0) * ((pi / 19.0) ** (i % 10)) * (n / 19.0)
        toplam_deger += terim / (i ** 1.1)
    
    ham_veri = ("KUKNER_STABLE_FIX::" + str(toplam_deger)).encode('utf-8')
    return hashlib.sha256(ham_veri).digest() # 32 Byte / 256-bit anahtar

# Güvenli Akış Şifreleme (XOR Counter Mode)
def sifrele_metin(text, key_bytes):
    text_bytes = text.encode('utf-8')
    output_bytes = bytearray()
    block_size = 32
    
    for i in range(0, len(text_bytes), block_size):
        chunk = text_bytes[i:i+block_size]
        counter_input = key_bytes + i.to_bytes(4, 'big')
        keystream_block = hashlib.sha256(counter_input).digest()
        
        for b_idx, b in enumerate(chunk):
            output_bytes.append(b ^ keystream_block[b_idx])
            
    return base64.b64encode(output_bytes).decode('utf-8')

def coz_metin(b64_encoded_str, key_bytes):
    try:
        encrypted_bytes = base64.b64decode(b64_encoded_str)
        output_bytes = bytearray()
        block_size = 32
        
        for i in range(0, len(encrypted_bytes), block_size):
            chunk = encrypted_bytes[i:i+block_size]
            counter_input = key_bytes + i.to_bytes(4, 'big')
            keystream_block = hashlib.sha256(counter_input).digest()
            
            for b_idx, b in enumerate(chunk):
                output_bytes.append(b ^ keystream_block[b_idx])
                
        return output_bytes.decode('utf-8')
    except Exception:
        return None

# --- 1. BÖLÜM: ŞİFRELEME ---
st.markdown("---")
st.subheader("🔐 1. Metin Şifreleme (Encrypt)")
gizli_mesaj = st.text_area("Şifrelenecek Gizli Metni Girin:", "Vazife Malullüğü ve Güvenli Veri Testi", key="input_gizli_mesaj")

if st.button("Veriyi Şifrele", key="btn_sifrele_islem"):
    if gizli_mesaj:
        anahtar = ozel_kdf_uret(n_val, terim_sayisi)
        sifreli_b64 = sifrele_metin(gizli_mesaj, anahtar)
        
        st.success("Şifreleme Başarılı!")
        st.text_input("Üretilen 256-bit Anahtar (Hex):", value=anahtar.hex(), key="out_anahtar_hex")
        st.text_area("Şifrelenmiş Veri (Kopyala ve Sakla):", value=sifreli_b64, key="out_sifreli_veri")
    else:
        st.warning("Lütfen şifrelenecek bir metin yazın.")

# --- 2. BÖLÜM: ÇÖZME ---
st.markdown("---")
st.subheader("🔓 2. Şifrelenmiş Veriyi Çözme (Decrypt)")
sifreli_giris = st.text_area("Şifrelenmiş Veriyi Buraya Yapıştırın:", key="input_sifreli_coz")

if st.button("Veriyi Çöz", key="btn_coz_islem"):
    if sifreli_giris:
        anahtar = ozel_kdf_uret(n_val, terim_sayisi)
        cozulen_veri = coz_metin(sifreli_giris.strip(), anahtar)
        
        if cozulen_veri:
            st.success("Çözme Başarılı!")
            st.text_area("Orijinal Metin:", value=cozulen_veri, key="out_orijinal_metin")
        else:
            st.error("Çözme başarısız! Parametreler (n veya terim sayısı) yanlış ya da veri bozuk.")
    else:
        st.warning("Lütfen çözülecek veriyi girin.")
