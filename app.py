import streamlit as st
import hashlib
import hmac
import secrets
import base64
import math
from decimal import Decimal, getcontext
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ============================================================
# KÜKNER CRYPTO STUDIO PRO
# ============================================================
#
# MATHEMATICAL CORE
#
#                 100
#        K(n) =  ------ × 19^n
#                  π
#
# The mathematical sequence is NOT used as a raw cipher.
# It is transformed into cryptographic material and combined
# with a random salt before deriving the AES-256-GCM key.
#
# ============================================================


APP_NAME = "KÜKNER Crypto Studio Pro"
VERSION = "2.0"

MAGIC = b"KUKNER19"
VERSION_BYTE = b"\x02"

SALT_SIZE = 32
NONCE_SIZE = 12
KEY_SIZE = 32

# High precision for the mathematical engine.
getcontext().prec = 300

PI = Decimal(
    "3.14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
)


# ============================================================
# 1. KÜKNER 19 MATHEMATICAL ENGINE
# ============================================================

def kukner_formula(n: int) -> Decimal:
    """
    K(n) = (100 / pi) * 19^n
    """
    return (Decimal(100) / PI) * (Decimal(19) ** n)


def fractional_part(value: Decimal) -> Decimal:
    """
    Returns only the fractional part.
    """
    return value - value.to_integral_value()


def kukner_decimal_stream(
    password: str,
    iterations: int = 256
) -> bytes:
    """
    Generates deterministic cryptographic material from
    the user's formula.

    K(n) = 100/pi * 19^n

    The decimal/fractional information is hashed instead
    of being directly converted into characters.
    """

    password_bytes = password.encode("utf-8")

    engine = hashlib.sha512()

    # Mathematical seed
    seed = hashlib.sha512(
        b"KUKNER-19-ENGINE" +
        password_bytes
    ).digest()

    engine.update(seed)

    for n in range(1, iterations + 1):

        value = kukner_formula(n)

        fraction = fractional_part(value)

        # Keep a stable high-precision decimal representation.
        decimal_string = format(
            fraction,
            "f"
        )

        block = (
            n.to_bytes(8, "big") +
            decimal_string.encode("ascii")
        )

        block_hash = hashlib.sha512(
            b"KUKNER19-BLOCK" +
            seed +
            block
        ).digest()

        engine.update(block_hash)

        # Feedback mechanism
        seed = hashlib.sha512(
            seed +
            block_hash +
            n.to_bytes(8, "big")
        ).digest()

    return engine.digest()


# ============================================================
# 2. ADDITIONAL 19 MIXING
# ============================================================

def kukner_19_mixer(
    material: bytes,
    rounds: int = 19
) -> bytes:
    """
    Additional 19-round cryptographic mixing layer.
    """

    state = material

    for i in range(1, rounds + 1):

        state = hashlib.sha512(
            b"KUKNER-MIX-19" +
            i.to_bytes(4, "big") +
            state
        ).digest()

    return state


# ============================================================
# 3. KEY DERIVATION
# ============================================================

def derive_key(
    password: str,
    salt: bytes,
    iterations: int = 256
) -> bytes:

    password_bytes = password.encode("utf-8")

    # Your mathematical formula
    mathematical_material = kukner_decimal_stream(
        password,
        iterations
    )

    # Additional 19-round mixing
    mixed = kukner_19_mixer(
        mathematical_material,
        19
    )

    # Combine everything
    combined = (
        b"KUKNER-CRYPTO-STUDIO-PRO" +
        password_bytes +
        salt +
        mathematical_material +
        mixed
    )

    # Final KDF
    #
    # PBKDF2 adds a conventional password-hardening layer.
    #
    key = hashlib.pbkdf2_hmac(
        "sha512",
        combined,
        salt,
        300_000,
        dklen=KEY_SIZE
    )

    return key


# ============================================================
# 4. PASSWORD STRENGTH
# ============================================================

def password_strength(password: str):

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
# 5. ENCRYPT
# ============================================================

def encrypt_bytes(
    data: bytes,
    password: str
) -> bytes:

    salt = secrets.token_bytes(SALT_SIZE)

    nonce = secrets.token_bytes(NONCE_SIZE)

    key = derive_key(
        password,
        salt
    )

    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        data,
        MAGIC
    )

    package = (
        MAGIC +
        VERSION_BYTE +
        salt +
        nonce +
        ciphertext
    )

    return package


# ============================================================
# 6. DECRYPT
# ============================================================

def decrypt_bytes(
    package: bytes,
    password: str
) -> bytes:

    minimum_size = (
        len(MAGIC) +
        1 +
        SALT_SIZE +
        NONCE_SIZE +
        16
    )

    if len(package) < minimum_size:
        raise ValueError(
            "Geçersiz veya bozuk KÜKNER şifreli veri."
        )

    if package[:len(MAGIC)] != MAGIC:
        raise ValueError(
            "Bu veri KÜKNER Crypto Studio Pro formatında değil."
        )

    position = len(MAGIC)

    version = package[position:position + 1]
    position += 1

    if version != VERSION_BYTE:
        raise ValueError(
            "Desteklenmeyen KÜKNER veri sürümü."
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

    ciphertext = package[position:]

    key = derive_key(
        password,
        salt
    )

    aes = AESGCM(key)

    try:

        plaintext = aes.decrypt(
            nonce,
            ciphertext,
            MAGIC
        )

    except Exception:

        raise ValueError(
            "Şifre çözülemedi. Parola yanlış "
            "veya veri değiştirilmiş olabilir."
        )

    return plaintext


# ============================================================
# 7. TEXT ENCRYPTION
# ============================================================

def encrypt_text(
    text: str,
    password: str
) -> str:

    package = encrypt_bytes(
        text.encode("utf-8"),
        password
    )

    return base64.urlsafe_b64encode(
        package
    ).decode("ascii")


# ============================================================
# 8. TEXT DECRYPTION
# ============================================================

def decrypt_text(
    encoded: str,
    password: str
) -> str:

    try:

        package = base64.urlsafe_b64decode(
            encoded.encode("ascii")
        )

    except Exception:

        raise ValueError(
            "Şifreli metin Base64 formatında değil."
        )

    plaintext = decrypt_bytes(
        package,
        password
    )

    return plaintext.decode("utf-8")


# ============================================================
# 9. HEX / HASH INFORMATION
# ============================================================

def sha512_hex(data: bytes) -> str:

    return hashlib.sha512(data).hexdigest()


def calculate_formula_preview():

    values = []

    for n in range(1, 11):

        value = kukner_formula(n)

        values.append({
            "n": n,
            "K(n)": format(value, ".40E"),
            "Virgül sonrası": format(
                fractional_part(value),
                ".30f"
            )
        })

    return values


# ============================================================
# 10. UI
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔐",
    layout="wide"
)


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("🔐 KÜKNER Crypto Studio Pro")

st.caption(
    f"Matematiksel çekirdek: 100 ÷ π × 19ⁿ  |  "
    f"Sürüm {VERSION}"
)


st.markdown(
    """
    ### KÜKNER 19 Engine

    **K(n) = (100 / π) × 19ⁿ**

    Matematiksel dizi, kriptografik anahtar üretim
    katmanına dahil edilir.
    """
)


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Sistem")

    mode = st.radio(
        "İşlem",
        [
            "🔒 Metin Şifrele",
            "🔓 Metin Çöz",
            "📁 Dosya Şifrele",
            "📂 Dosya Çöz",
            "🧮 19 Engine"
        ]
    )

    st.divider()

    st.write("### 🔐 Güvenlik")

    st.write(
        "AES-256-GCM"
    )

    st.write(
        "SHA-512"
    )

    st.write(
        "PBKDF2-HMAC-SHA512"
    )

    st.write(
        "KÜKNER 19 Engine"
    )


# ============================================================
# PASSWORD INPUT
# ============================================================

if mode != "🧮 19 Engine":

    password = st.text_input(
        "🔑 Anahtar / Parola",
        type="password"
    )

    if password:

        strength, score = password_strength(
            password
        )

        st.progress(
            min(score / 7, 1.0)
        )

        st.caption(
            f"Parola gücü: **{strength}**"
        )


# ============================================================
# TEXT ENCRYPT
# ============================================================

if mode == "🔒 Metin Şifrele":

    st.header("🔒 Metin Şifreleme")

    text = st.text_area(
        "Metin",
        height=300,
        placeholder="Şifrelemek istediğiniz metni yazın..."
    )

    if st.button(
        "🔐 KÜKNER 19 İLE ŞİFRELE",
        use_container_width=True
    ):

        if not text:

            st.warning(
                "Lütfen şifrelenecek metni girin."
            )

        elif len(password) < 12:

            st.warning(
                "En az 12 karakterlik güçlü bir parola kullanın."
            )

        else:

            encrypted = encrypt_text(
                text,
                password
            )

            st.success(
                "Şifreleme başarıyla tamamlandı."
            )

            st.text_area(
                "Şifreli Metin",
                encrypted,
                height=300
            )

            st.download_button(
                "⬇️ Şifreli Metni Kaydet",
                encrypted,
                file_name="KUKNER19_ENCRYPTED.txt",
                mime="text/plain",
                use_container_width=True
            )


# ============================================================
# TEXT DECRYPT
# ============================================================

elif mode == "🔓 Metin Çöz":

    st.header("🔓 Metin Şifre Çözme")

    encrypted = st.text_area(
        "Şifreli Metin",
        height=300,
        placeholder="KÜKNER şifreli metni buraya yapıştırın..."
    )

    if st.button(
        "🔓 ŞİFREYİ ÇÖZ",
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

                st.text_area(
                    "Çözülen Metin",
                    result,
                    height=300
                )

            except Exception as error:

                st.error(
                    str(error)
                )


# ============================================================
# FILE ENCRYPTION
# ============================================================

elif mode == "📁 Dosya Şifrele":

    st.header("📁 Dosya Şifreleme")

    uploaded = st.file_uploader(
        "Şifrelenecek dosyayı seçin"
    )

    if uploaded:

        st.info(
            f"Dosya: {uploaded.name}  |  "
            f"{uploaded.size:,} byte"
        )

        if st.button(
            "🔐 DOSYAYI ŞİFRELE",
            use_container_width=True
        ):

            if len(password) < 12:

                st.warning(
                    "En az 12 karakterlik parola kullanın."
                )

            else:

                data = uploaded.read()

                encrypted = encrypt_bytes(
                    data,
                    password
                )

                output_name = (
                    uploaded.name +
                    ".kukner19"
                )

                st.success(
                    "Dosya başarıyla şifrelendi."
                )

                st.download_button(
                    "⬇️ Şifreli Dosyayı İndir",
                    encrypted,
                    file_name=output_name,
                    mime="application/octet-stream",
                    use_container_width=True
                )


# ============================================================
# FILE DECRYPTION
# ============================================================

elif mode == "📂 Dosya Çöz":

    st.header("📂 Dosya Şifre Çözme")

    uploaded = st.file_uploader(
        "KÜKNER şifreli dosyayı seçin",
        type=["kukner19"]
    )

    if uploaded:

        if st.button(
            "🔓 DOSYAYI ÇÖZ",
            use_container_width=True
        ):

            try:

                encrypted_data = uploaded.read()

                decrypted = decrypt_bytes(
                    encrypted_data,
                    password
                )

                original_name = uploaded.name

                if original_name.endswith(
                    ".kukner19"
                ):

                    original_name = (
                        original_name[
                            :-len(".kukner19")
                        ]
                    )

                else:

                    original_name += ".decrypted"

                st.success(
                    "Dosyanın şifresi çözüldü."
                )

                st.download_button(
                    "⬇️ Çözülmüş Dosyayı İndir",
                    decrypted,
                    file_name=original_name,
                    mime="application/octet-stream",
                    use_container_width=True
                )

            except Exception as error:

                st.error(
                    str(error)
                )


# ============================================================
# 19 ENGINE
# ============================================================

elif mode == "🧮 19 Engine":

    st.header("🧮 KÜKNER 19 Mathematical Engine")

    st.latex(
        r"""
        K(n)=\frac{100}{\pi}\times19^n
        """
    )

    st.write(
        "Formülün ilk 10 iterasyonu:"
    )

    data = calculate_formula_preview()

    for item in data:

        with st.expander(
            f"n = {item['n']}"
        ):

            st.write(
                "K(n):"
            )

            st.code(
                item["K(n)"]
            )

            st.write(
                "Virgül sonrası:"
            )

            st.code(
                item["Virgül sonrası"]
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "KÜKNER Crypto Studio Pro — KÜKNER 19 Engine"
)

st.caption(
    "Matematiksel formül: K(n) = (100 / π) × 19ⁿ"
)
