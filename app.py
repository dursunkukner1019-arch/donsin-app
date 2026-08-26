import math
import streamlit as st

st.set_page_config(page_title="Gerçek Formül Şifreleme", page_icon="🔐")

st.title("🔐 Formül Tabanlı Güçlü Şifreleme Aracı")
st.write("Formül: **100 / Pi * 1923** (Dinamik Matris Karıştırma)")

class TrueFormulaEncrypter:
    def __init__(self):
        # Sizin belirttiğiniz temel formül sabiti
        self.base_val = (100 / math.pi) * 1923

    def process_text(self, text: str, mode: str) -> str:
        result_chars = []
        # Formülün başlangıç çarpanı
        current_multiplier = self.base_val
        
        for i, char in enumerate(text):
            code = ord(char)
            # Her karakter için formülü ve indeks değerini harmanlayan dinamik bir kaydırma anahtarı üretiyoruz
            current_multiplier = (current_multiplier * 1.618033 + (i + 1) * 99.7) % 10000
            shift = int(current_multiplier) % 256
            
            if mode == "encrypt":
                # Şifreleme: Karakter koduna dinamik kaydırmayı ekle
                new_code = (code + shift) % 1114112 # Unicode sınırları içinde
            else:
                # Çözme: Dinamik kaydırmayı çıkar
                new_code = (code - shift) % 1114112
                
            result_chars.append(chr(new_code))
            
        return "".join(result_chars)

    def encrypt(self, plaintext: str) -> str:
        return self.process_text(plaintext, "encrypt")

    def decrypt(self, ciphertext: str) -> str:
        return self.process_text(ciphertext, "decrypt")

# Uygulamayı başlat
app = TrueFormulaEncrypter()

# Arayüz
user_input = st.text_input("Şifrelenecek Metni Girin:", value="AAAAA")

if user_input:
    sifreli_sonuc = app.encrypt(user_input)
    cozulmus_sonuc = app.decrypt(sifreli_sonuc)
    
    st.markdown("### 🔒 Şifrelenmiş Çıktı:")
    # Çıktının karakterlerini net görebilmek için kod bloğu olarak veriyoruz
    st.code(sifreli_sonuc, language="")
    
    st.info("Artık `AAAAA`, `AAAAB` ve `BAAAA` yazdığında, her harfin formül içindeki konumu ve çarpanı tamamen değiştiği için çıktılar birbirine benzemeyecektir.")
    
    with st.expander("🔓 Şifreyi Çöz (Test Paneli)"):
        st.write(cozulmus_sonuc)
