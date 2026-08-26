import math
import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Özel Şifreleme Uygulaması", page_icon="🔐")

st.title("🔐 Formül Tabanlı Şifreleme Uygulaması")
st.write("Formül: **100 / Pi * 1923** kullanılarak oluşturulmuştur.")

class StreamlitEncrypter:
    def __init__(self):
        self.base_constant = (100 / math.pi) * 1923

    def _get_shift(self, index: int) -> int:
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

app = StreamlitEncrypter()

# Kullanıcı Arayüzü (Girdi Alanı)
metin = st.text_input("Şifrelenecek Metni Girin:", "AAAAA")

if metin:
    sifreli = app.encrypt(metin)
    cozulmus = app.decrypt(sifreli)
    
    st.subheader("Sonuçlar:")
    st.code(sifreli, language="")
    
    st.success("Şifreleme başarıyla tamamlandı!")
    
    # Çözülmüş hali kontrol için
    with st.expander("Şifreyi Çöz (Test Et)"):
        st.write(cozulmus)
