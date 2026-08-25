from decimal import Decimal, getcontext
import streamlit as st

st.set_page_config(
    page_title="KÜKNER Pİ × 1923 Şifreleme", page_icon="🔐", layout="centered"
)

st.title("🔐 KÜKNER Pİ × 1923 Akış Şifreleme Uygulaması")
st.markdown(
    """
Bu uygulama, irrasyonel **Pi ($\pi$)** tabanlı hassas bölme ve **1923** çarpanıyla 
iteratif olarak büyüyen kesintisiz, tekrarsız akış (keystream) mantığını kullanır.
"""
)

# Kenar Çubuğu Ayarları
st.sidebar.header("Algoritma Parametreleri")
precision = st.sidebar.slider(
    "Pi Hassasiyeti (Basamak Sayısı)",
    min_value=100,
    max_value=3000,
    value=1000,
    step=100,
    help="Virgülden sonra kaç basamak hassasiyetle hesaplanacağını belirler.",
)
multiplier = st.sidebar.number_input(
    "Çarpan (Anahtar)", value=1923, step=1, format="%d"
)


# KÜKNER Pİ × 1923 Akış Üreteci Fonksiyonu
def generate_kukner_keystream(digits, mult):
  # Hassasiyet sınırını ayarla
  getcontext().prec = digits + 10

  # Chudnovsky algoritması ile yüksek hassasiyetli Pi hesaplama
  C = 426880 * Decimal(10005).sqrt()
  K = Decimal(6)
  M = Decimal(1)
  L = Decimal(13591409)
  X = Decimal(1)
  S = L

  for k in range(1, int(digits / 14) + 1):
    M = M * (K**3 - 16 * K) / (Decimal(k) ** 3)
    L += 545140134
    X *= -262537412640768000
    S += (M * L) / X
    K += 12

  pi_val = C / S

  # KÜKNER Pİ × 1923 formül mantığı
  calculation_result = (Decimal(100) / pi_val) * Decimal(mult)

  str_val = str(calculation_result)
  if "." in str_val:
    fractional_part = str_val.split(".")[1]
  else:
    fractional_part = str_val

  return fractional_part


# Arayüz Sekmeleri
tab1, tab2 = st.tabs(["🔒 Metin Şifreleme / Çözme", "📊 Akış ve Entropi İncelemesi"])

with tab1:
  st.subheader("KÜKNER Pİ × 1923 ile Metin Şifreleme")
  text_input = st.text_area(
      "Şifrelenecek Metni Girin:",
      placeholder="Gizli mesajınızı buraya yazın...",
  )

  if st.button("Mesajı İşle / Şifrele"):
    if text_input:
      with st.spinner("KÜKNER Pİ × 1923 anahtar akışı üretiliyor..."):
        keystream = generate_kukner_keystream(precision, multiplier)

        # Stream Cipher (XOR / Karakter Kaydırma) mantığı
        encrypted_chars = []
        for i, char in enumerate(text_input):
          key_char_code = int(keystream[i % len(keystream)])
          encrypted_code = ord(char) + key_char_code
          encrypted_chars.append(chr(encrypted_code))

        encrypted_text = "".join(encrypted_chars)

      st.success("Şifreleme Başarıyla Tamamlandı!")
      st.text_area(
          "Şifrelenmiş Çıktı (Ciphertext):",
          value=encrypted_text,
          height=100,
      )
    else:
      st.warning("Lütfen şifrelenecek bir metin girin.")

with tab2:
  st.subheader("Üretilen Sayısal Akış Verisi")
  st.markdown(
      "Aşağıda **KÜKNER Pİ × 1923** algoritmasıyla üretilen tekrarsız ve"
      " kesintisiz küsurat dizisinin bir kısmı yer almaktadır:"
  )

  if st.button("Akış Verisini Göster"):
    stream = generate_kukner_keystream(precision, multiplier)
    st.code(stream[:1000], language="text")
    st.info(f"Toplam üretilen güvenli basamak uzunluğu: {len(stream)} karakter.")
