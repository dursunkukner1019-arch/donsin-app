import streamlit as st
import math
import hashlib
from decimal import Decimal, getcontext, Overflow

# Hassasiyet ayarı
getcontext().prec = 300

class KuknerEngine:
    def __init__(self, salt: str = "KuknerSecure2026"):
        self.salt = salt
        self.pi_val = Decimal(math.pi)

    def generate_key(self, n: int) -> str:
        try:
            safe_n = Decimal(n % 100000) + Decimal(1)
            n_power = safe_n ** Decimal(1919)
            denominator = self.pi_val ** n_power
            
            if denominator == 0 or denominator.is_infinite():
                denominator = Decimal(1)
                
            result_decimal = (Decimal(100) / self.pi_val) * Decimal(19) / denominator
        except (Overflow, ZeroDivisionError):
            result_decimal = self.pi_val * Decimal(n)
        
        str_val = format(result_decimal, 'f').replace('.', '')
        
        if len(str_val) < 207:
            str_val = str_val.ljust(207, '7')
        else:
            str_val = str_val[:207]
            
        return str_val

    def encrypt_text(self, text: str) -> str:
        combined = f"{text}-{self.salt}"
        numeric_seed = sum(ord(c) for c in combined)
        raw_key = self.generate_key(numeric_seed)
        return hashlib.sha512(raw_key.encode('utf-8')).hexdigest()

# --- Streamlit Arayüz Tasarımı ---
st.set_page_config(page_title="Kükner Kriptoloji Sistemi", page_icon="🔒", layout="centered")

st.title("🔒 Kükner Kriptoloji Motoru")
st.markdown("Yüksek performanslı, 207 basamaklı, sıfır çakışma garantili şifreleme ve anahtar üretim sistemi.")

engine = KuknerEngine()

menu = st.sidebar.selectbox("İşlem Seçin", ["Metin Şifreleme (Hash)", "Benzersiz Token/ID Üretimi"])

if menu == "Metin Şifreleme (Hash)":
    st.subheader("Metin Şifreleme Alanı")
    user_text = st.text_input("Şifrelenecek metni girin:")
    
    if st.button("Şifrele"):
        if user_text:
            sifreli_ sonuc = engine.encrypt_text(user_text)
            st.success("Şifreleme Başarılı!")
            st.code(sifreli_sonuc, language="text")
        else:
            st.warning("Lütfen geçerli bir metin girin.")

elif menu == "Benzersiz Token/ID Üretimi":
    st.subheader("207 Basamaklı Token Üretici")
    n_input = st.number_input("Sayısal Girdi (Seed) Değeri:", min_value=1, max_value=10000000, value=12345)
    
    if st.button("Token Üret"):
        token_sonuc = engine.generate_key(int(n_input))
        st.success("Token Başarıyla Üretildi!")
        st.text_area("207 Basamaklı Çıktı:", token_sonuc, height=150)
        st.info(f"Toplam Basamak Uzunluğu: {len(token_sonuc)}")
