import math

class SimpleEncrypter:
    def __init__(self):
        # Sizin formülünüz: 100 / Pi * 1923
        self.base_constant = (100 / math.pi) * 1923

    def _get_shift(self, index: int) -> int:
        current_val = (self.base_constant * (index + 1)) * 1.618033
        return int(current_val) % 94

    def encrypt(self, plaintext: str) -> str:
        encrypted_chars = []
        for i, char in enumerate(plaintext):
            code = ord(char)
            if 32 <= code <= 126:
                shift = self._get_shift(i)
                new_code = 32 + (code - 32 + shift) % 94
                encrypted_chars.append(chr(new_code))
            else:
                encrypted_chars.append(char)
        return "".join(encrypted_chars)

    def decrypt(self, ciphertext: str) -> str:
        decrypted_chars = []
        for i, char in enumerate(ciphertext):
            code = ord(char)
            if 32 <= code <= 126:
                shift = self._get_shift(i)
                new_code = 32 + (code - 32 - shift) % 94
                decrypted_chars.append(chr(new_code))
            else:
                decrypted_chars.append(char)
        return "".join(decrypted_chars)

# --- UYGULAMA BAŞLATICI ---
if __name__ == "__main__":
    app = SimpleEncrypter()
    
    girdi = "AAAAA"
    print("--- ŞİFRELEME TESTİ BAŞLADI ---")
    print(f"Orijinal Girdi : {girdi}")
    
    sifreli = app.encrypt(girdi)
    print(f"Şifreli Çıktı  : {sifreli}")
    
    cozulmus = app.decrypt(sifreli)
    print(f"Çözülen Metin  : {cozulmus}")
    print("--------------------------------")
    
    # Konsolun hemen kapanmaması için kullanıcıdan girdi bekletiyoruz
    input("Uygulama tamamlandı. Çıkmak için Enter tuşuna basın...")
