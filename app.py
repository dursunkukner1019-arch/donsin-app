import streamlit as st
import hashlib
import hmac
import secrets
import base64
from decimal import Decimal, getcontext


# ============================================================
# KÜKNER CRYPTO STUDIO PRO
# ============================================================
#
# KÜKNER FORMÜLÜ:
#
#                 100
#        K(n) =  ----- × 19^n
#                  π
#
# ============================================================

st.set_page_config(
    page_title="KÜKNER Crypto Studio Pro",
    page_icon="🔐",
    layout="wide"
)

APP_NAME = "KÜKNER Crypto Studio Pro"

MAGIC = b"KUKNER19"
VERSION = b"\x05"

SALT_SIZE = 32
NONCE_SIZE = 16
TAG_SIZE = 32
KEY_SIZE = 32

getcontext().prec = 300

PI = Decimal(
    "3.14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
)


# ============================================================
# KÜKNER FORMÜLÜ
# ============================================================

def kukner_formula(n):

    return (
        Decimal(100) / PI
    ) * (
        Decimal(19) ** n
    )


def fractional_digits(value, digits=100):

    text = format(value, "f")

    if "." not in text:
        return "0"

    return text.split(".", 1)[1][:digits]


# ============================================================
# KÜKNER 19 ENGINE
# ============================================================

def kukner_engine(password, rounds=128):

    password_bytes = password.encode("utf-8")

    state = hashlib.sha512(
        b"KUKNER-19-ENGINE" +
        password_bytes
    ).digest()

    for n in range(1, rounds + 1):

        value = kukner_formula(n)

        fraction = fractional_digits(
            value,
            100
        )

        block = (
            n.to_bytes(8, "big") +
            fraction.encode("ascii")
        )

        state = hashlib.sha512(
            b"KUKNER19" +
            state +
            block
        ).digest()

    return state


# ============================================================
# 19 KATMANLI KARIŞTIRMA
# ============================================================

def mix_19(data):

    state = data

    for i in range(1, 20):

        state = hashlib.sha512(
            b"KUKNER-MIX-19" +
            i.to_bytes(2, "big") +
            state
        ).digest()

    return state


# ============================================================
# ANAHTAR ÜRETİMİ
# ============================================================

def derive_key(password, salt):

    mathematical_data = kukner_engine(
        password,
        128
    )

    mixed_data = mix_19(
        mathematical_data
    )

    seed = (
        b"KUKNER-CRYPTO-STUDIO-PRO" +
        password.encode("utf-8") +
        salt +
        mathematical_data +
        mixed_data
    )

    return hashlib.pbkdf2_hmac(
        "sha512",
        seed,
        salt,
        300000,
        dklen=KEY_SIZE
    )


# ============================================================
# ANAHTAR AKIŞI
# ============================================================

def generate_keystream(key, nonce, length):

    result = bytearray()

    counter = 0

    while len(result) < length:

        block = hmac.new(
            key,
            b"KUKNER-STREAM" +
            nonce +
            counter.to_bytes(8, "big"),
            hashlib.sha256
        ).digest()

        result.extend(block)

        counter += 1

    return bytes(
        result[:length]
    )


# ============================================================
# XOR
# ============================================================

def xor_bytes(data, stream):

    return bytes(
        a ^ b
        for a, b in zip(data, stream)
    )


# ============================================================
# ŞİFRELEME
# ============================================================

def encrypt_text(text, password):

    data = text.encode("utf-8")

    # Her işlemde farklı salt
    salt = secrets.token_bytes(
        SALT_SIZE
    )

    # Her işlemde farklı nonce
    nonce = secrets.token_bytes(
        NONCE_SIZE
    )

    key = derive_key(
        password,
        salt
    )

    stream = generate_keystream(
        key,
        nonce,
        len(data)
    )

    ciphertext = xor_bytes(
        data,
        stream
    )

    header = (
        MAGIC +
        VERSION +
        salt +
        nonce
    )

    tag = hmac.new(
        key,
        header + ciphertext,
        hashlib.sha256
    ).digest()

    package = (
        header +
        ciphertext +
        tag
    )

    return base64.urlsafe_b64encode(
        package
    ).decode("ascii")


# ============================================================
# ŞİFRE ÇÖZME
# ============================================================

def decrypt_text(encoded, password):

    try:

        package = base64.urlsafe_b64decode(
            encoded.encode("ascii")
        )

    except Exception:

        raise ValueError(
            "Şifreli veri geçerli değil."
        )

    minimum = (
        len(MAGIC) +
        1 +
        SALT_SIZE +
        NONCE_SIZE +
        TAG_SIZE
    )

    if len(package) < minimum:

        raise ValueError(
            "Şifreli veri eksik veya bozuk."
        )

    # KÜKNER başlık kontrolü
    if package[:len(MAGIC)] != MAGIC:

        raise ValueError(
            "Bu veri KÜKNER formatında değil."
        )

    position = len(MAGIC)

    version = package[
        position:
        position + 1
    ]

    position += 1

    if version != VERSION:

        raise ValueError(
            "Desteklenmeyen KÜKNER sürümü."
        )

    salt = package[
        position:
        position + SALT_SIZE
    ]

    position += SALT_SIZE

    nonce = package[
        position:
        position + NONCE_SIZE
    ]

    position += NONCE_SIZE

    encrypted = package[position:]

    ciphertext = encrypted[
        :-TAG_SIZE
    ]

    received_tag = encrypted[
        -TAG_SIZE:
    ]

    key = derive_key(
        password,
        salt
    )

    header = (
        MAGIC +
        VERSION +
        salt +
        nonce
    )

    expected_tag = hmac.new(
        key,
        header + ciphertext,
        hashlib.sha256
    ).digest()

    # Veri değiştirilmiş mi?
    if not hmac.compare_digest(
        received_tag,
        expected_tag
    ):

        raise ValueError(
            "Şifre çözülemedi.\n\n"
            "Parola yanlış olabilir veya "
            "şifreli veri değiştirilmiş olabilir."
        )

    stream = generate_keystream(
        key,
        nonce,
        len(ciphertext)
    )

    plaintext = xor_bytes(
        ciphertext,
        stream
    )

    try:

        return plaintext.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise ValueError(
            "Şifre çözülen veri geçerli UTF-8 metni değil."
        )


# ============================================================
# PAROLA GÜCÜ
# ============================================================

def password_strength(password):

    score = 0

    if len(password) >= 8:
        score += 1

    if len(password) >= 12:
        score += 1

    if len(password) >= 16:
        score += 1

    if any(c.islower() for c in password):
        score += 1

    if any(c.isupper() for c in password):
        score += 1

    if any(c.isdigit() for c in password):
        score += 1

    if any(not c.isalnum() for c in password):
        score += 1

    if score <= 2:
        return "Zayıf", score

    if score <= 4:
        return "Orta", score

    if score <= 6:
        return "Güçlü", score

    return "Çok Güçlü", score


# ============================================================
# BAŞLIK
# ============================================================

st.title("🔐 KÜKNER Crypto Studio Pro")

st.markdown(
    """
    ### KÜKNER 19 Engine

    **K(n) = (100 ÷ π) × 19ⁿ**

    Matematiksel çekirdek, anahtar üretim sistemine
    dahil edilerek şifreleme sürecinin bir parçası
    olarak kullanılır.
    """
)

st.divider()


# ============================================================
# SEKME SİSTEMİ
# ============================================================

tab_encrypt, tab_decrypt, tab_engine = st.tabs(
    [
        "🔒 METİN ŞİFRELE",
        "🔓 ŞİFRE ÇÖZ",
        "🧮 19 ENGINE"
    ]
)


# ============================================================
# 1. METİN ŞİFRELE
# ============================================================

with tab_encrypt:

    st.header(
        "🔒 Metin Şifreleme"
    )

    password_encrypt = st.text_input(
        "🔑 Gizli Anahtar",
        type="password",
        key="encrypt_password",
        placeholder="En az 12 karakter"
    )

    if password_encrypt:

        strength, score = password_strength(
            password_encrypt
        )

        st.progress(
            score / 7
        )

        st.caption(
            f"Parola gücü: **{strength}**"
        )

    text = st.text_area(
        "📝 Şifrelenecek Metin",
        height=250,
        key="encrypt_text",
        placeholder=(
            "Buraya şifrelemek istediğiniz "
            "metni yazın..."
        )
    )

    if st.button(
        "🔐 KÜKNER 19 İLE ŞİFRELE",
        type="primary",
        use_container_width=True,
        key="encrypt_button"
    ):

        if not text:

            st.warning(
                "Lütfen şifrelenecek metni girin."
            )

        elif len(password_encrypt) < 12:

            st.warning(
                "Güvenlik için en az 12 karakterlik "
                "bir parola kullanın."
            )

        else:

            encrypted = encrypt_text(
                text,
                password_encrypt
            )

            st.success(
                "✅ Metin başarıyla şifrelendi."
            )

            st.markdown(
                "### 🔐 Şifreli Metin"
            )

            # Streamlit code alanı otomatik
            # KOPYALA düğmesi gösterir.
            st.code(
                encrypted,
                language=None
            )

            st.download_button(
                "⬇️ Şifreli Metni Kaydet",
                encrypted,
                file_name="KUKNER19_ENCRYPTED.txt",
                mime="text/plain",
                use_container_width=True
            )

            st.info(
                "📋 Şifreli metni yukarıdaki kutunun "
                "sağ üstündeki kopyalama simgesinden "
                "kopyalayabilirsiniz."
            )


# ============================================================
# 2. ŞİFRE ÇÖZ
# ============================================================

with tab_decrypt:

    st.header(
        "🔓 Şifre Çözme"
    )

    st.info(
        "Şifreleme sırasında kullandığınız "
        "aynı parolayı girin."
    )

    password_decrypt = st.text_input(
        "🔑 Gizli Anahtar",
        type="password",
        key="decrypt_password",
        placeholder="Şifreleme sırasında kullandığınız parola"
    )

    encrypted_input = st.text_area(
        "🔐 Şifreli Metin",
        height=280,
        key="decrypt_text",
        placeholder=(
            "Şifreleme sekmesinde oluşturduğunuz "
            "şifreli metni buraya yapıştırın..."
        )
    )

    if st.button(
        "🔓 ŞİFREYİ ÇÖZ",
        type="primary",
        use_container_width=True,
        key="decrypt_button"
    ):

        if not encrypted_input:

            st.warning(
                "Lütfen şifreli metni girin."
            )

        elif not password_decrypt:

            st.warning(
                "Lütfen gizli anahtarı girin."
            )

        else:

            try:

                decrypted = decrypt_text(
                    encrypted_input.strip(),
                    password_decrypt
                )

                st.success(
                    "✅ Şifre başarıyla çözüldü."
                )

                st.markdown(
                    "### 📄 Çözülen Metin"
                )

                # Bunun da KOPYALA düğmesi vardır.
                st.code(
                    decrypted,
                    language=None
                )

                st.download_button(
                    "⬇️ Çözülen Metni Kaydet",
                    decrypted,
                    file_name="KUKNER19_DECRYPTED.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except ValueError as error:

                st.error(
                    str(error)
                )

            except Exception:

                st.error(
                    "Şifre çözme sırasında beklenmeyen "
                    "bir hata oluştu."
                )


# ============================================================
# 3. 19 ENGINE
# ============================================================

with tab_engine:

    st.header(
        "🧮 KÜKNER 19 Mathematical Engine"
    )

    st.latex(
        r"K(n)=\frac{100}{\pi}\times19^n"
    )

    st.write(
        "KÜKNER formülünün ilk 19 değeri:"
    )

    for n in range(1, 20):

        value = kukner_formula(n)

        with st.expander(
            f"19 Engine — n = {n}"
        ):

            st.write(
                "K(n) ="
            )

            st.code(
                format(
                    value,
                    ".70E"
                ),
                language=None
            )

            st.write(
                "Virgülden sonraki basamaklar:"
            )

            st.code(
                fractional_digits(
                    value,
                    100
                ),
                language=None
            )

    st.divider()

    st.subheader(
        "KÜKNER işlem zinciri"
    )

    st.markdown(
        """
        **100 ÷ π × 19ⁿ**

        ↓

        **KÜKNER 19 Engine**

        ↓

        **SHA-512**

        ↓

        **19 katmanlı karıştırma**

        ↓

        **Parola + Salt**

        ↓

        **PBKDF2-HMAC-SHA512**

        ↓

        **KÜKNER anahtar üretimi**

        ↓

        **Şifreli çıktı + bütünlük doğrulaması**
        """
    )


# ============================================================
# ALT BİLGİ
# ============================================================

st.divider()

st.caption(
    "KÜKNER Crypto Studio Pro"
)

st.caption(
    "K(n) = (100 ÷ π) × 19ⁿ"
)
