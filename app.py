from decimal import Decimal, getcontext
import streamlit as st

st.set_page_config(
    page_title="KÜKNER Pİ × 1923 Şifreleme", page_icon="🔐", layout="centered"
)

st.title("🔐 KÜKNER Pİ × 1923 Şifreleme ve Çözme")
st.markdown(
    """
Bu uygulama, irrasyonel **Pi ($\pi$)** tabanlı ve **1923** çarpanıyla 
çalışan akış şifreleme sistemidir.
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
)
multiplier = st.sidebar.number_input(
    "Çarpan (Anahtar)", value=1923, step=1, format="%d"
)


# KÜKNER Pİ × 1923 Akış Üreteci Fonksiyonu
def generate_kukner_keystream(digits, mult):
  getcontext().prec = digits + 10

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
  calculation_result = (Decimal(100) / pi_val) * Decimal(mult)

  str_val = str(calculation_result)
  if "." in str_val:
    fractional_part = str_val.split(".")[1]
  else:
    fractional_part = str_val

  return fractional_part


# İşlem Modu Seçimi (Şifrele veya Çöz)
islem_tipi = st.radio(
    "İşlem Türünü Seçin:", ["🔒 Metni Şifrele", "🔓 Şifreyi Çöz"]
)

input_text = st.text_area(
    "İşlem Yapılacak Metin:",
    placeholder="Metninizi buraya yapıştırın...",
)

if st.button("İşlemi Başlat"):
  if input_text:
    keystream = generate_kukner_keystream(precision, multiplier)
    sonuc_chars = []

    for i, char in enumerate(input_text):
      key_char_code = int(keystream[i % len(keystream)])

      if islem_tipi == "🔒 Metni Şifrele":
        # Şifrelerken anahtar değerini ekle
        yeni_kod = ord(char) + key_char_code
      else:
        # Şifre çözerken anahtar değerini çıkar
        yeni_kod = ord(char) - key_char_code

      sonuc_chars.append(chr(yeni_kod))

    sonuc_metin = "".join(sonuc_chars)

    st.success("İşlem Başarıyla Tamamlandı!")
    if islem_tipi == "🔒 Metni Şifrele":
      st.text_area("Şifrelenmiş Çıktı:", value=sonuc_metin, height=100)
    else:
      st.text_area("Çözülmüş Orijinal Metin:", value=sonuc_metin, height=100)
  else:
    st.warning("Lütfen metin alanını boş bırakmayın.")
