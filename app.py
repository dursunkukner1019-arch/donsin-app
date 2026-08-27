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
# KÜKNER MATEMATİKSEL FORMÜLÜ
#
#              100
# K(n) =  ----------- × 19^n
#                π
#
# ============================================================


APP_NAME = "KÜKNER Crypto Studio Pro"
VERSION = "4.0"

MAGIC = b"KUKNER19"
VERSION_BYTE = b"\x04"

SALT_SIZE = 32
NONCE_SIZE = 16
TAG_SIZE = 32
KEY_SIZE = 32

# Yüksek hassasiyet
getcontext().prec = 300

PI = Decimal(
    "3.14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
)


# ============================================================
# KÜKNER FORMÜLÜ
# ============================================================

def kukner_formula(n):
    """
    K(n) = (100 / π) × 19^n
    """

    return (
        Decimal(100) / PI
    ) * (
        Decimal(19) ** n
    )


# ============================================================
# VİRGÜLDEN SONRAKİ BASAMAKLAR
# ============================================================

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

    password_bytes = password.encode("utf-8")

    # Senin matematiksel formülün
    mathematical_data = kukner_engine(
        password,
        128
    )

    # 19 katmanlı karıştırma
    mixed_data = mix_19(
        mathematical_data
    )

    seed = (
        b"KUKNER-CRYPTO-STUDIO-PRO" +
        password_bytes +
        salt +
        mathematical_data +
        mixed_data
    )

    # Paroladan güçlü anahtar türetme
    key = hashlib.pbkdf2_hmac(
        "sha512",
        seed,
        salt,
        300000,
        dklen=KEY_SIZE
    )

    return key


# ============================================================
# ŞİFRELEME AKIŞI
# ============================================================

def generate_keystream(key, nonce, length):

    output = bytearray()

    counter = 0

    while len(output) < length:

        block = hmac.new(
            key,
            (
                b"KUKNER-STREAM" +
                nonce +
                counter.to_bytes(8, "big")
            ),
            hashlib.sha256
        ).digest()

        output.extend(block)

        counter += 1

    return bytes(
        output[:length]
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
# METİN / VERİ ŞİFRELE
# ============================================================

def encrypt_bytes(data, password):

    # Her şifrelemede yeni salt
    salt = secrets.token_bytes(
        SALT_SIZE
    )

    # Her şifrelemede yeni nonce
    nonce = secrets.token_bytes(
        NONCE_SIZE
    )

    key = derive_key(
        password,
        salt
    )

    keystream = generate_keystream(
        key,
        nonce,
        len(data)
    )

    ciphertext = xor_bytes(
        data,
        keystream
    )

    # Başlık
    header = (
        MAGIC +
        VERSION_BYTE +
        salt +
        nonce
    )

    # HMAC bütünlük kontrolü
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

    return package


# ============================================================
# VERİ ŞİFRE ÇÖZ
# ============================================================

def decrypt_bytes(package, password):

    minimum_length = (
        len(MAGIC) +
        1 +
        SALT_SIZE +
        NONCE_SIZE +
        TAG_SIZE
    )

    if len(package) < minimum_length:

        raise ValueError(
            "Şifreli veri eksik veya bozuk."
        )

    # MAGIC kontrolü
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

    if version != VERSION_BYTE:

        raise ValueError(
            "Desteklenmeyen KÜKNER sürümü."
        )

    # Salt
    salt = package[
        position:
        position + SALT_SIZE
    ]

    position += SALT_SIZE

    # Nonce
    nonce = package[
        position:
        position + NONCE_SIZE
    ]

    position += NONCE_SIZE

    # Ciphertext + tag
    encrypted_part = package[position:]

    ciphertext = encrypted_part[:-TAG_SIZE]

    received_tag = encrypted_part[-TAG_SIZE:]

    key = derive_key(
        password,
        salt
    )

    header = (
        MAGIC +
        VERSION_BYTE +
        salt +
        nonce
    )

    expected_tag = hmac.new(
        key,
        header + ciphertext,
        hashlib.sha256
    ).digest()

    # Önce bütünlük kontrolü
    if not hmac.compare_digest(
        received_tag,
        expected_tag
    ):

        raise ValueError(
            "Şifre çözülemedi. "
            "Parola yanlış veya veri değiştirilmiş."
        )

    keystream = generate_keystream(
        key,
        nonce,
        len(ciphertext)
    )

    plaintext = xor_bytes(
        ciphertext,
        keystream
    )

    return plaintext


# ============================================================
# METİN ŞİFRELE
# ============================================================

def encrypt_text(text, password):

    data = text.encode(
        "utf-8"
    )

    package = encrypt_bytes(
        data,
        password
    )

    return base64.urlsafe_b64encode(
        package
    ).decode(
        "ascii"
    )


# ============================================================
# METİN ŞİFRE ÇÖZ
# ============================================================

def decrypt_text(encoded, password):

    try:

        package = base64.urlsafe_b64decode(
            encoded.encode("ascii")
        )

    except Exception:

        raise ValueError(
            "Şifreli metin geçerli değil."
        )

    plaintext = decrypt_bytes(
        package,
        password
    )

    return plaintext.decode(
        "utf-8"
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

    if any(
        c.islower()
        for c in password
    ):
        score += 1

    if any(
        c.isupper()
        for c in password
    ):
        score += 1

    if any(
        c.isdigit()
        for c in password
    ):
        score += 1

    if any(
        not c.isalnum()
        for c in password
    ):
        score += 1

    if score <= 2:
        return "Zayıf", score

    if score <= 4:
        return "Orta", score

    if score <= 6:
        return "Güçlü", score

    return "Çok Güçlü", score


# ============================================================
# STREAMLIT AYARLARI
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# BAŞLIK
# ============================================================

st.title(
    "🔐 KÜKNER Crypto Studio Pro"
)

st.caption(
    "KÜKNER 19 Engine • "
    "100 ÷ π × 19ⁿ"
)


# ============================================================
# MENÜ
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ KÜKNER CRYPTO"
    )

    mode = st.radio(
        "İşlem seçin",
        [
            "🔒 Metin Şifrele",
            "🔓 Metin Çöz",
            "🧮 19 Engine"
        ]
    )

    st.divider()

    st.markdown(
        "### 🔐 Sistem"
    )

    st.write(
        "KÜKNER 19 Engine"
    )

    st.write(
        "SHA-512"
    )

    st.write(
        "PBKDF2-HMAC-SHA512"
    )

    st.write(
        "HMAC-SHA256"
    )

    st.write(
        "Rastgele Salt + Nonce"
    )


# ============================================================
# METİN ŞİFRELEME
# ============================================================

if mode == "🔒 Metin Şifrele":

    st.header(
        "🔒 Metin Şifreleme"
    )

    password = st.text_input(
        "🔑 Gizli Anahtar",
        type="password",
        placeholder="Güçlü bir parola girin"
    )

    if password:

        strength, score = password_strength(
            password
        )

        st.progress(
            score / 7
        )

        st.caption(
            f"Parola gücü: **{strength}**"
        )

    text = st.text_area(
        "Şifrelenecek Metin",
        height=280,
        placeholder=(
            "Şifrelemek istediğiniz "
            "metni buraya yazın..."
        )
    )

    if st.button(
        "🔐 KÜKNER 19 İLE ŞİFRELE",
        type="primary",
        use_container_width=True
    ):

        if not text:

            st.warning(
                "Lütfen metin girin."
            )

        elif len(password) < 12:

            st.warning(
                "En az 12 karakterlik "
                "bir parola kullanın."
            )

        else:

            encrypted = encrypt_text(
                text,
                password
            )

            st.success(
                "Şifreleme tamamlandı."
            )

            st.markdown(
                "### 🔐 Şifreli Metin"
            )

            # Streamlit'in code alanında
            # otomatik KOPYALA düğmesi vardır.
            st.code(
                encrypted,
                language=None
            )

            st.download_button(
                "⬇️ Şifreli Metni Kaydet",
                encrypted,
                file_name=(
                    "KUKNER19_ENCRYPTED.txt"
                ),
                mime="text/plain",
                use_container_width=True
            )

            st.info(
                "Yukarıdaki kod alanındaki "
                "📋 kopyalama düğmesini kullanabilirsiniz."
            )


# ============================================================
# METİN ŞİFRE ÇÖZME
# ============================================================

elif mode == "🔓 Metin Çöz":

    st.header(
        "🔓 Metin Şifre Çözme"
    )

    password = st.text_input(
        "🔑 Gizli Anahtar",
        type="password",
        placeholder="Şifreleme sırasında kullandığınız parola"
    )

    encrypted = st.text_area(
        "Şifreli Metin",
        height=280,
        placeholder=(
            "KÜKNER tarafından oluşturulan "
            "şifreli metni buraya yapıştırın..."
        )
    )

    if st.button(
        "🔓 ŞİFREYİ ÇÖZ",
        type="primary",
        use_container_width=True
    ):

        if not encrypted:

            st.warning(
                "Şifreli metni girin."
            )

        elif not password:

            st.warning(
                "Parolayı girin."
            )

        else:

            try:

                result = decrypt_text(
                    encrypted,
                    password
                )

                st.success(
                    "Şifre başarıyla çözüldü."
                )

                st.markdown(
                    "### 📄 Çözülen Metin"
                )

                # Bunun da kopyalama düğmesi vardır.
                st.code(
                    result,
                    language=None
                )

                st.download_button(
                    "⬇️ Çözülen Metni Kaydet",
                    result,
                    file_name="KUKNER19_DECRYPTED.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except ValueError as error:

                st.error(
                    str(error)
                )


# ============================================================
# 19 ENGINE
# ============================================================

elif mode == "🧮 19 Engine":

    st.header(
        "🧮 KÜKNER 19 Mathematical Engine"
    )

    st.latex(
        r"""
        K(n)=\frac{100}{\pi}\times19^n
        """
    )

    st.markdown(
        """
        ### KÜKNER matematiksel çekirdeği

        **100 ÷ π × 19ⁿ**

        Sistem, formülün ürettiği yüksek hassasiyetli
        matematiksel veriyi SHA-512 tabanlı anahtar
        üretim zincirine dahil eder.
        """
    )

    st.divider()

    st.subheader(
        "İlk 19 değer"
    )

    for n in range(1, 20):

        value = kukner_formula(n)

        with st.expander(
            f"n = {n}"
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
        "KÜKNER 19 işlem zinciri"
    )

    st.markdown(
        """
        **100 ÷ π × 19ⁿ**

        ↓

        Yüksek hassasiyetli matematiksel dizi

        ↓

        SHA-512

        ↓

        19 katmanlı karıştırma

        ↓

        Parola + rastgele salt

        ↓

        PBKDF2-HMAC-SHA512

        ↓

        KÜKNER anahtar üretimi

        ↓

        HMAC doğrulamalı şifreleme
        """
    )

    st.info(
        "Matematiksel formül KÜKNER 19 Engine'in "
        "özgün bileşenidir. Şifreleme güvenliği için "
        "formülün yanında standart kriptografik "
        "hash/HMAC yapı taşları kullanılmıştır."
    )


# ============================================================
# ALT BİLGİ
# ============================================================

st.divider()

st.caption(
    "KÜKNER Crypto Studio Pro"
)

st.caption(
    "K(n) = (100 / π) × 19ⁿ"
)
