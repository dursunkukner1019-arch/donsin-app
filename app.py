import math
import sys

class PerfectFormulaEncrypter:
    def __init__(self):
        # İstediğiniz formül: 100 / Pi * 1923
        self.base_constant = (100 / math.pi) * 1923

    def _get_shift(self, index: int) -> int:
        """
        Formülü sürekli çarparak her karakter için benzersiz kaydırma üretir.
        """
        # Formülü index'e göre sürekli çarpıp güncelliyoruz
        current_val = (self.base_constant * (index + 1)) * 1.618033
        return int(current_val) % 94  # Yazdırılabilir ASCII karakter aralığı için

    def encrypt(self, plaintext: str) -> str:
        """
        Metni formüle göre şifreler.
        """
        encrypted_chars = []
        for i, char in enumerate(plaintext):
            code = ord(char)
            # Sadece normal karakterleri şifrele (32 ile 126 arası yazdırılabilir ASCII)
            if 32 <= code <= 126:
                shift = self._get_shift(i)
                # 94 karakterlik aralıkta kaydırma yapıyoruz
                new_code = 32 + (code - 32 + shift) % 94
                encrypted_chars.append(chr(new_code))
            else:
                encrypted_chars.append(char)
                
        return "".join(encrypted_chars)

    def decrypt(self, ciphertext: str) -> str:
        """
        Şifrelenmiş metni formülü tersine işleterek çözer.
        """
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
        Harici kütüphane gerektirmeden panoya kopyalama (Windows/Mac/Linux uyumlu).
        """
        try:
            from tkinter import Tk
            r = Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update()
            r.destroy()
            print("[Bilgi] Şifreli metin başarıyla panoya kopyalandı! (Ctrl+V yapabilirsiniz)")
        except Exception:
            print("[Bilgi] Panoya kopyalanamadı ama şifreli metin aşağıdadır.")

# --- UYGULAMAYI ÇALIŞTIRMA ---
if __name__ == "__main__":
    app = PerfectFormulaEncrypter()
    
    girdi = "AAAAA"
    print(f"Orijinal Girdi : {girdi}")
    
    # Şifreleme
    sifreli = app.encrypt(girdi)
    print(f"Şifreli Çıktı  : {sifreli}")
    
    # Panoya Kopyala
    app.copy_to_clipboard(sifreli)
    
    # Çözüm Testi
    cozulmus = app.decrypt(sifreli)
    print(f"Çözülen Metin  : {cozulmus}")
