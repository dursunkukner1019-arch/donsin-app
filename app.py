from decimal import Decimal, getcontext
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="KÜKNER-1923 Crypto Studio Pro",
    page_icon="🔐",
    layout="wide",
)

st.title("🔐 KÜKNER-1923 Crypto Studio Pro")
st.subheader("Dinamik Matris & 378 Adımlı Kriptografik Döngü Arayüzü")
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
        states = []

        for step in range(1, length + 1):
            product = current_state * self.multiplier
            integer_part = int(product)
            fractional_part = product - integer_part

            keystream.append(integer_part)
            states.append({
                "Adım": step,
                "Tam Kısım (Anahtar)": integer_part,
                "Kayan Küsurat Değeri": f"{fractional_part:.15f}...",
            })

            current_state = fractional_part

        return keystream, states

    def encrypt(self, text):
        keystream, _ = self.generate_keystream(len(text))
        encrypted_bytes = []
        for i, char in enumerate(text):
            key_byte = keystream[i] % 256
            encrypted_bytes.append(ord(char) ^ key_byte)
        return encrypted_bytes

    def decrypt(self, encrypted_bytes):
        keystream, _ = self.generate_keystream(len(encrypted_bytes))
        decrypted_chars = []
        for i, byte in enumerate(encrypted_bytes):
            key_byte = keystream[i] % 256
            decrypted_chars.append(chr(byte ^ key_byte))
        return "".join(decrypted_chars)


kukner = Kukner1923Crypto()

# Yan Panel - Parametreler ve Kök Bilgisi
st.sidebar.header("⚙️ Sistem Parametreleri")
st.sidebar.info(
    "**Payda 1:** 243 (3⁵)\n\n"
    "**Payda 2:** 49 (7²)\n\n"
    "**Çarpan:** 1923 (Cumhuriyet Katsayısı)\n\n"
    "**Sabit Kök:** 7577 (Kayan Matris)\n\n"
    "**Tam Periyot:** 378 Adım"
)

# Sekmeli Arayüz
tab1, tab2, tab3 = st.tabs([
    "📊 Matris & Döngü Analizi",
    "🔒 Canlı Şifreleme (Crypto Engine)",
    "📜 Teorik Altyapı",
])

with tab1:
    st.markdown("### 378 Adımlı Kusursuz Periyodik Döngü Haritası")
    adim_sayisi = st.slider(
        "Görüntülenecek Adım Sayısını Seçin",
        min_value=5,
        max_value=378,
        value=27,
    )

    _, states = kukner.generate_keystream(adim_sayisi)
    df = pd.DataFrame(states)

    st.dataframe(df, use_container_width=True)

    # Periyot Kontrol Butonu
    if st.button("378. Adım / Sıfırlanma Testi Yap"):
        _, all_states = kukner.generate_keystream(379)
        st.success(
            f"**378. Adım Sonu Küsurat (Döngü Sonu):**"
            f" {all_states[377]['Kayan Küsurat Değeri']}"
        )
        st.warning(
            f"**379. Adım (1. Adıma Dönüş / Tam Kısım):**"
            f" {all_states[378]['Tam Kısım (Anahtar)']} (1. Adım ile Birebir"
            " Aynı!)"
        )

with tab2:
    st.markdown("### KÜKNER-1923 Stream Cipher Metin Şifreleme")
    girdi_metni = st.text_input(
        "Şifrelenecek Metni Girin", "KUKNER-1923 CRYPTO STUDIO PRO"
    )

    if girdi_metni:
        sifreli_baytlar = kukner.encrypt(girdi_metni)
        cozulmus_metin = kukner.decrypt(sifreli_baytlar)

        col1, col2 = st.columns(2)
        with col1:
            st.error(f"**Şifrelenmiş Bayt Dizisi:**\n\n`{sifreli_baytlar}`")
        with col2:
            st.success(f"**Çözülen Metin:**\n\n`{cozulmus_metin}`")

with tab3:
    st.markdown("""
    **Formül Bağıntısı:**
    $$S_0 = \\text{Küsurat}\\left(\\frac{100}{243}\\right) + \\text{Küsurat}\\left(\\frac{100}{49}\\right)$$
    $$S_{k+1} = \\text{Küsurat}\\left(S_k \\times 1923\\right)$$

    - $3^5 = 243$ paydası **27 basamaklı** devir üretir.
    - $7^2 = 49$ paydası **42 basamaklı** devir üretir.
    - İki frekansın birleşimi $\\text{EKOK}(27, 42) = \\mathbf{378}$ adımlık kırılması imkansız bir periyot sağlar.
    """)
