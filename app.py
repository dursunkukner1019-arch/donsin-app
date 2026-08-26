import math
import streamlit as st

st.set_page_config(page_title="Çakışmasız Formül Şifreleme", page_icon="🔐")

st.title("🔐 Çakışmasız Formül Tabanlı Şifreleme Aracı")
st.write("Formül: **100 / Pi * 1923** ile sürekli çarpım ve çakışmasızlık mimarisi.")

class CollisionFreeEncrypter:
    def __init__(self):
        # Temel formülümüz
        self.base_constant = (100 / math.pi) * 1923

    def _get_unique_multiplier(self, index: int) -> int:
        """
        1 milyon işlemde dahi çakışma üretmeyecek şekilde 
        formülü sürekli çarparak benzersiz bir büyük sayı üretir.
        """
        # Sürekli çarpım ve hash benzeri genişleme adımı
        val = self.base_constant * (index + 1)
        # Sayının ondalık kısımlarını ve büyüklüğünü benzersiz bir tamsayıya çeviriyoruz
        unique_factor = int(val * 1000000) ^ (index * 7919)
        return abs(unique_factor)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        
        encrypted_tokens = []
        for i, char in enumerate(plaintext):
            char_code = ord(char)
            # Formülden gelen çakışmasız çarpan
            multiplier = self._get_unique_multiplier(i)
            
            # Karakter kodunu devasa ve benzersiz bir formül havuzuyla harmanlıyoruz
            # Çakışmayı önlemek için geniş bir matematiksel aralık kullanıyoruz
            encrypted_code = char_code + (multiplier % 100000)
            encrypted_tokens.append(str(encrypted_code))
            
        # Çakışmayı ve karışıklığı önlemek için tokenleri özel bir ayraçla birleştiriyoruz
        return "-".join(encrypted_tokens)

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
            
        try:
            tokens = ciphertext.split("-")
            decrypted_chars = []
            
            for i, token in enumerate(tokens):
                encrypted_code = int(token)
                multiplier = self._get_unique_multiplier(i)
                
                # Şifreleme adımını tam tersine çeviriyoruz
                char_code = encrypted_code - (multiplier % 100000)
                decrypted_chars.append(chr(char_code))
                
            return "".join(decrypted_chars)
        except Exception:
            return "[Hata] Şifre çözülemedi veya format bozuk!"

# Uygulamayı Başlat
app = CollisionFreeEncrypter()

# Arayüz
user_input = st.text_input("Şifrelenecek Metni Girin:", value="AAAAA")

if user_input:
    sifreli_sonuc = app.encrypt(user_input)
    cozulmus_sonuc = app.decrypt(sifreli_sonuc)
    
    st.markdown("### 🔒 Çakışmasız Şifrelenmiş Çıktı:")
    st.code(sifreli_sonuc, language="")
    
    st.info("Bu mimari sayesinde `AAAAA`, `AAAAB` veya `BAAAA` girdiğinde, formülün sürekli çarpım mantığı devreye girer ve 1 milyon işlemde bile asla çakışma yaratmayan tamamen benzersiz bir çıktı kümesi oluşur.")
    
    with st.expander("🔓 Şifreyi Çöz (Test Paneli)"):
        st.write(cozulmus_sonuc)
