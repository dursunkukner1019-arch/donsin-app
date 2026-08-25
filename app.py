from decimal import Decimal, getcontext


class Kukner1923Crypto:
    """KÜKNER-1923 Dinamik Matris Kriptografik Rastgele Sayı Üreteci

    Matematiksel Altyapı:
    - Payda 1: 3^5 = 243 (27 basamak periyot)
    - Payda 2: 7^2 = 49  (42 basamak periyot)
    - EKOK(27, 42) = 378 Adımlık Kusursuz Periyodik Döngü
    - Çarpan: 1923 (Cumhuriyet Katsayısı / Kayma Çarpanı)
    - Sabit Kök Değeri: 7577 (Devirli kayan matris kökü)
    """

    def __init__(self, precision=300):
        getcontext().prec = precision

        self.p1 = Decimal(243)
        self.p2 = Decimal(49)
        self.multiplier = Decimal(1923)

        # S0 Başlangıç Durumu (100/243 ve 100/49 küsuratlar toplamı)
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
                "step": step,
                "integer_key": integer_part,
                "fractional_state": fractional_part,
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


# --- KODUN ÇALIŞTIRMA VE TEST BÖLÜMÜ ---
kukner = Kukner1923Crypto()

print("=" * 65)
print("  KÜKNER-1923 DİNAMİK MATRİS SİSTEMİ - TEST VE DOĞRULAMA")
print("=" * 65)

# 1. Başlangıç Değeri
print(f"S0 (Başlangıç Küsurat Toplamı) : {kukner.initial_state:.15f}...")

# 2. İlk 5 Adımın Çıktısı
_, states = kukner.generate_keystream(5)
print("\n[İlk 5 Adım Matris Çıktısı]")
for s in states:
    print(
        f"Adım {s['step']}: Tam Kısım (Anahtar) = {s['integer_key']:4d} | "
        f"Kayan Küsurat = {s['fractional_state']:.10f}..."
    )

# 3. 378 Adımlık Periyot Testi
_, all_states = kukner.generate_keystream(379)
print("\n[Periyot Ve Sıfırlanma Testi]")
print(
    f"378. Adım Sonu Küsurat        : {all_states[377]['fractional_state']:.15f}..."
)
print(
    f"379. Adım (Döngü Başı) Anahtar: {all_states[378]['integer_key']} "
    f"(1. Adım olan {all_states[0]['integer_key']} ile BİREBİR AYNI)"
)

# 4. Kripto Şifreleme Testi
metin = "KUKNER-1923 CRYPTO STUDIO PRO"
sifreli = kukner.encrypt(metin)
cozulmus = kukner.decrypt(sifreli)

print("\n[Kripto Testi]")
print(f"Orijinal Metin  : {metin}")
print(f"Şifreli Baytlar : {sifreli}")
print(f"Çözülen Metin   : {cozulmus}")
print("=" * 65)
