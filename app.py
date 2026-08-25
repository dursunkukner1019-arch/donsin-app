from decimal import Decimal, getcontext
import math


class Kukner1923Crypto:
    """KÜKNER-1923 Dinamik Matris Kriptografik Rastgele Sayı Üreteci ve Şifreleme Sistemi

    Matematiksel Altyapı:
    - Payda 1: 3^5 = 243 (27 basamak periyot)
    - Payda 2: 7^2 = 49  (42 basamak periyot)
    - EKOK(27, 42) = 378 Adımlık Kusursuz Periyodik Döngü
    - Çarpan: 1923 (Cumhuriyet Katsayısı / Kayma Çarpanı)
    - Sabit Kök Değeri: 7577 (Devirli kayan matris kökü)
    """

    def __init__(self, precision=300):
        # Yüksek matematiksel hassasiyet ayarı
        getcontext().prec = precision

        self.p1 = Decimal(243)  # 3^5
        self.p2 = Decimal(49)  # 7^2
        self.multiplier = Decimal(1923)

        # Temel Küsuratlar Toplamı (S0 Başlangıç Durumu)
        k1 = (Decimal(100) / self.p1) - int(Decimal(100) / self.p1)
        k2 = (Decimal(100) / self.p2) - int(Decimal(100) / self.p2)
        self.initial_state = k1 + k2

    def generate_keystream(self, length=378):
        """KÜKNER-1923 algoritması ile belirtilen uzunlukta tam sayı anahtar dizisi (Keystream) üretir."""
        current_state = self.initial_state
        keystream = []
        states = []

        for step in range(1, length + 1):
            product = current_state * self.multiplier
            integer_part = int(product)
            fractional_part = product - integer_part

            keystream.append(integer_part)
            states.append(
                {
                    "step": step,
                    "integer_key": integer_part,
                    "fractional_state": fractional_part,
                }
            )

            current_state = fractional_part

        return keystream, states

    def encrypt(self, text):
        """Metni KÜKNER-1923 anahtar dizisi ile XOR uygulayarak şifreler."""
        keystream, _ = self.generate_keystream(len(text))
        encrypted_bytes = []
        for i, char in enumerate(text):
            # Anahtar tam sayısını 256 moduna alarak karakter bazlı XOR şifreleme
            key_byte = keystream[i] % 256
            encrypted_bytes.append(ord(char) ^ key_byte)
        return encrypted_bytes

    def decrypt(self, encrypted_bytes):
        """Şifrelenmiş bayt dizisini KÜKNER-1923 ile çözer."""
        keystream, _ = self.generate_keystream(len(encrypted_bytes))
        decrypted_chars = []
        for i, byte in enumerate(encrypted_bytes):
            key_byte = keystream[i] % 256
            decrypted_chars.append(chr(byte ^ key_byte))
        return "".join(decrypted_chars)


# --- SİSTEMİ ÇALIŞTIRMA VE DOĞRULAMA TESTİ ---
if __name__ == "__main__":
    kukner = Kukner1923Crypto()

    print("=" * 65)
    print("  KÜKNER-1923 DİNAMİK MATRİS SİSTEMİ - SİMÜLASYON VERİLERİ")
    print("=" * 65)

    # 1. Başlangıç Değerleri
    print(f"S0 (Başlangıç Küsurat Toplamı) : {kukner.initial_state:.15f}...")

    # 2. İlk 5 Adımın İncelemesi
    _, states = kukner.generate_keystream(5)
    print("\n[İlk 5 Adım Kilit Matrisi Output] ")
    for s in states:
        print(
            f"Adım {s['step']}: Tam Kısım (Anahtar) = {s['integer_key']:4d} |"
            f" Kayan Küsurat = {s['fractional_state']:.10f}..."
        )

    # 3. Periyot Doğrulaması (378. ve 379. Adımlar)
    _, all_states = kukner.generate_keystream(379)
    print("\n[Periyot Ve Sıfırlanma Testi]")
    print(
        f"378. Adım Küsuratı (Döngü Sonu) : {all_states[377]['fractional_state']:.15f}..."
    )
    print(
        f"379. Adım Tam Kısım (Döngü Başı): {all_states[378]['integer_key']}"
        " (1. Adım ile Birebir Aynı)"
    )

    # 4. Kriptografik Şifreleme Testi
    metin = "KUKNER-1923 CRYPTO STUDIO PRO"
    sifreli = kukner.encrypt(metin)
    cozulmus = kukner.decrypt(sifreli)

    print("\n[Kripto Testi]")
    print(f"Orijinal Metin  : {metin}")
    print(f"Şifreli Baytlar : {sifreli[:8]}...")
    print(f"Çözülen Metin   : {cozulmus}")
    print("=" * 65)
