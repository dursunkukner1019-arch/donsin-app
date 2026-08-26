import math
import sys

class BulletproofEncrypter:
    def __init__(self):
        # Sizin belirttiğiniz temel formül: 100 / Pi * 1923
        self.base_constant = (100 / math.pi) * 1923

    def _get_shift(self, index: int) -> int:
        """
        Formülü sürekli çarparak her karakter için dinamik kaydırma üretir.
        """
        # Sürekli çarpım mantığı
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

    def copy_to_clipboard(self, text: str):
        """
        Hata vermeyen, güvenli panoya kopyalama denemesi.
        """
        try:
            # Önce pyperclip deneyelim
            import pyperclip
            pyperclip.copy(text)
            print("[Bilgi] Şifreli metin panoya kopyalandı!")
            return
        except Exception:
            pass

        try:
            # Olmazsa Tkinter deneyelim
            from tkinter import Tk
            root = Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            print("[Bilgi] Şifreli metin panoya kopyalandı!")
            return
        except Exception:
            # Hiçbiri çalışmazsa program çökmez, sadece bilgi verir
            print("[Bilgi] Pano kopyalama bu ortamda desteklenmiyor, şifreli metin ekrandadır.")

# --- TEST KODU ---
if __name__ == "__main__":
    app = BulletproofEncrypter()
    
    girdi = "AAAAA"
    print(f"Orijinal Girdi : {girdi}")
    
    sifreli = app.encrypt(girdi)
    print(f"Şifreli Çıktı  : {sifreli}")
    
    app.copy_to_clipboard(sifreli)
    
    cozulmus = app.decrypt(sifreli)
    print(f"Çözülen Metin  : {cozulmus}")
