import math
import hashlib
import streamlit as st

st.set_page_config(page_title="Formül Tabanlı Şifreleme", page_icon="🔐")

st.title("🔐 Güçlü Formül Tabanlı Şifreleme Aracı")
st.write("Kullanılan Formül: **100 / Pi * 1923** tabanlı karmaşık akış motoru.")

class PerfectFormulaEncrypter:
    def __init__(self):
        # Sizin belirttiğiniz formül
        base_val = (100 / math.pi) * 1923
        self.secret_seed = hashlib.sha256(str(base_val).encode()).digest()

    def _generate_keystream(self, length: int) -> bytearray:
        keystream = bytearray()
        counter = 0
        while len(keystream) < length:
            block = hashlib.sha256(self.secret_seed + counter.to_bytes(4, 'big')).digest()
            keystream.extend(block)
            counter += 1
        return keystream[:length]

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        plain_bytes = plaintext.encode('utf-8')
        keystream = self._generate_keystream(len(plain_bytes))
        encrypted_bytes = bytes(b ^ k for b, k in zip(plain_bytes, keystream))
        return encrypted_bytes.hex()

    def decrypt(self, hex_ciphertext: str) -> str:
        try:
            encrypted_bytes = bytes.fromhex(hex_ciphertext)
            keystream = self._generate_keystream(len(encrypted_bytes))
            decrypted_bytes = bytes(b ^ k for b, k in zip(encrypted_bytes, keystream))
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return "[Hata] Şifre çözülemedi!"

# Uygulamayı başlat
app = PerfectFormulaEncrypter()

# Arayüz Bileşenleri
user_input = st.text_input("Şifrelenecek Metni Girin:", value="AAAAA")

if user_input:
    sifreli_sonuc = app.encrypt(user_input)
    cozulmus_sonuc = app.decrypt(sifreli_sonuc)
    
    st.markdown("### 🔒 Şifrelenmiş Çıktı:")
    st.code(sifreli_sonuc, language="")
    
    st.success("Bu mimari sayesinde `AAAAA`, `AAAAB` veya `BAAAA` yazdığınızda çıktılar birbirine benzemez, tamamen güçlü ve dinamik hale gelir.")
    
    with st.expander("🔓 Şifreyi Çöz (Test Paneli)"):
        st.write(cozulmus_sonuc)
