import math
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(page_title="Özel Şifreleme Uygulaması", page_icon="🔐", layout="centered")

st.title("🔐 Formül Tabanlı Şifreleme Aracı")
st.write("Kullanılan Formül: **100 / Pi * 1923** (Sürekli Çarpım Akış Mantığı)")

class FormulaWebEncrypter:
    def __init__(self):
        # Sizin belirttiğiniz temel formül sabiti
        self.base_constant = (100 / math.pi) * 1923

    def _get_shift(self, index: int) -> int:
        # Formülü sürekli güncelleyerek her harf için özgün bir kaydırma üretir
        current_val = (self.base_constant * (index + 1)) * 1.618033
        return int(current_val) % 94

    def encrypt(self, plaintext: str) -> str:
        encrypted_chars = []
        for i, char in enumerate(plaintext):
            code = ord(char)
            if 32 <= code <= 126:
                shift = self._get_shift(i)
                new_code = 32 + (code - 32 + shift) % 94
                encrypted_chars.append(chr(new_code))
            else:
                encrypted_chars.append(char)
        return "".join(encrypted_chars)

    def decrypt(self, ciphertext: str) -> str:
        decrypted_chars = []
        for i, char in enumerate(ciphertext):
            code = ord(char)
            if 32 <= code <= 126:
                shift = self._get_shift(i)
                new_code = 32 + (code - 32 - shift) % 94
                decrypted_chars.append(chr(new_code))
            else:
                decrypted_chars.append(char)
        return "".join(decrypted_chars)

# Uygulama Sınıfını Başlat
app = FormulaWebEncrypter()

# Kullanıcı Girdi Alanı
st.markdown("### Metin Girişi")
user_input = st.text_input("Şifrelenecek metni yazın:", value="AAAAA")

if user_input:
    sifreli_metin = app.encrypt(user_input)
    cozulmus_metin = app.decrypt(sifreli_metin)
    
    st.markdown("---")
    st.markdown("### 📤 Şifrelenmiş Sonuç")
    st.code(sifreli_metin, language="")
    
    # Küçük bir bilgi notu
    st.info("Girdiğiniz metindeki tek bir harf değiştiğinde (örneğin AAAA{A} yerine AAAA{B}), çıktının nasıl tamamen dinamik değiştiğini test edebilirsiniz.")
    
    with st.expander("🛠️ Şifreyi Çöz (Test Paneli)"):
        st.write("Çözülmüş Orijinal Metin:", cozulmus_metin)
