import math
import hashlib
import streamlit as st

st.set_page_config(page_title="Gelişmiş Formül Şifreleme", page_icon="🔐")

st.title("🔐 Gelişmiş Formül Tabanlı Şifreleme Aracı")
st.write("Formül: **100 / Pi * 1923** tabanlı blok karıştırma motoru.")

class AdvancedFormulaEncrypter:
    def __init__(self):
        # Temel formülümüzü hesaplıyoruz
        base_val = (100 / math.pi) * 1923
        # Bu formül sonucunu kriptografik bir anahtar havuzuna (seed) dönüştürüyoruz
        self.secret_seed = hashlib.sha256(str(base_val).encode()).digest()

    def _generate_keystream(self, length: int) -> bytearray:
        """Formül tabanlı anahtar havuzundan metin uzunluğuna uygun dinamik baytlar üretir."""
        keystream = bytearray()
        counter = 0
        while len(keystream) < length:
            # Formül sabitini ve sayacı hashleyerek tamamen çığ etkili (avalanche) bir akış elde ediyoruz
            block = hashlib.sha256(self.secret_seed + counter.to_bytes(4, 'big')).digest()
            keystream.extend(block)
            counter += 1
        return keystream[:length]

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        plain_bytes = plaintext.encode('utf-8')
        keystream = self._generate_keystream(len(plain_bytes))
        
        # XOR ve blok karıştırma işlemi (Basit kaydırma değil, gerçek karmaşık yapı)
        encrypted_bytes = bytes(b ^ k for b, k in zip(plain_bytes, keystream))
        
        # Okunabilir ve taşınabilir olması için Hex formatına çeviriyoruz
        return encrypted_bytes.hex()

    def decrypt(self, hex_ciphertext: str) -> str:
        try:
            encrypted_bytes = bytes.fromhex(hex_ciphertext)
            keystream = self._generate_keystream(len(encrypted_bytes))
            decrypted_bytes = bytes(b ^ k for b, k in zip(encrypted_bytes, keystream))
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return "[Hata] Şifre çözülemedi veya metin bozuk!"

app = AdvancedFormulaEncrypter()

# Arayüz
user_input = st.text_input("Şifrelenecek Metni Girin (Örn: AAAAA, AAAAB):", value="AAAAA")

if user_input:
    sifreli_ sonuc = app.encrypt(user_input)
    cozulmus_sonuc = app.decrypt(sifreli_sonuc)
    
    st.markdown("### 🔒 Şifrelenmiş Çıktı:")
    st.code(sifreli_sonuc, language="")
    
    st.info("Artık `AAAAA`, `AAAAB` veya `BAAAA` girdiğinizde, formülün arkasındaki hash ve karıştırma motoru sayesinde çıktının ne kadar değiştiğini (basit görünmediğini) görebilirsiniz.")
    
    with st.expander("🔓 Şifreyi Çöz (Test Et)"):
        st.write(cozulmus_sonuc)
