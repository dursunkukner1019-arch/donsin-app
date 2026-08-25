from decimal import Decimal, getcontext
import json
import streamlit as st

st.set_page_config(
    page_title="KÜKNER-1923 Crypto Studio Pro",
    page_icon="🔐",
    layout="wide",
)

st.title("🔐 KÜKNER-1923 Metin Şifreleme ve Çözme Arayüzü")
st.markdown("---")


class Kukner1923Crypto:

    def __init__(self, precision=300):
        getcontext().prec = precision
        self.p1 = Decimal(243)
        self.p2 = Decimal(49)
        self.multiplier = Decimal(1923)

        k1 = (Decimal(100) / self.p1) - int(Decimal(100) / self.p1)
        k2 = (Decimal(100) / self.p2) - int(Decimal(100) / self.p2)
        self.initial_state = k1 + k2

    def generate_keystream(self, length=378):
        current_state = self.initial_state
        keystream = []
        for _ in range(length):
            product = current_state * self.multiplier
            integer_part = int(product)
            fractional_part = product - integer_part
            keystream.append(integer_part)
            current_state = fractional_part
        return keystream

    def encrypt(self, text):
        keystream = self.generate_keystream(len(text))
        encrypted_bytes = []
        for i, char in enumerate(text):
            key_byte = keystream[i] % 256
            encrypted_bytes.append(ord(char) ^ key_byte)
        return encrypted_bytes

    def decrypt(self, encrypted_bytes):
        keystream = self.generate_keystream(len(encrypted_bytes))
        decrypted_chars = []
        for i, byte in enumerate(encrypted_bytes):
            key_byte = keystream[i] % 256
            decrypted_chars.append(chr(byte ^ key_byte))
        return "".join(decrypted_chars)


kukner = Kukner1923Crypto()

# Yan Panel Bilgisi
st.sidebar.header("⚙️ KÜKNER-1923 Bilgileri")
st.sidebar.info(
    "**Döngü Periyodu:** 378 Adım\n\n"
    "**Sabit Kök:** 7577\n\n"
    "**Çarpan:** 1923\n\n"
    "Bu panel üzerinden metinlerinizi güvenle şifreleyebilir veya şifrelenmiş"
    " verileri çözebilirsiniz."
)

tab1, tab2 = st.tabs(
    ["🔒 Metin Şifrele (Encrypt)", "🔓 Şifre Çöz (Decrypt)"]
)

# 1. SEKME: METİN ŞİFRELEME
with tab1:
    st.markdown("### Düz Metni KÜKNER-1923 ile Şifreleyin")
    metin_girdi = st.text_area(
        "Şifrelenecek Düz Metni Girin",
        value="46162217723898",
        height=100,
    )

    if st.button(" Metni Şifrele", type="primary"):
        if metin_girdi:
            sifreli_baytlar = kukner.encrypt(metin_girdi)
            st.success("Metin başarıyla şifrelendi!")

            # Kopyalanabilir çıktı formatı
            st.markdown("**Şifreli Veri (Şifre Çözme Sekmesine Kopyalayın):**")
            st.code(json.dumps(sifreli_baytlar), language="json")
        else:
            st.warning("Lütfen bir metin girin.")

# 2. SEKME: BİRBİRİNDEN BAĞIMSIZ ŞİFRE ÇÖZME
with tab2:
    st.markdown("### KÜKNER-1923 Şifreli Veriyi Çözün")
    sifreli_girdi = st.text_area(
        "Şifreli Bayt Dizisini Yapıştırın (Örn: [81, 104, 131, ...])",
        height=100,
    )

    if st.button("🔓 Şifreyi Çöz", type="primary"):
        if sifreli_girdi:
            try:
                # Girdiyi liste formatına dönüştür
                bayt_listesi = json.loads(sifreli_girdi)
                cozulmus_sonuc = kukner.decrypt(bayt_listesi)

                st.success("Şifre Başarıyla Çözüldü!")
                st.markdown("**Orijinal Metin:**")
                st.info(cozulmus_sonuc)
            except Exception as e:
                st.error(
                    "Geçersiz şifreli dizi formatı! Lütfen tam köşeli parantezli"
                    " liste yapıştırın. Örn: [81, 104, 131]"
                )
        else:
            st.warning("Lütfen şifreli veri yapıştırın.")
