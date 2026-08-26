import math

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class FormulaStreamEncrypter:
    def __init__(self):
        # Temel formülümüz: 100 / Pi * 1923
        self.base_constant = (100 / math.pi) * 1923

    def _generate_stream(self, length: int) -> list:
        """
        Formülü sürekli çarparak her karakter için benzersiz bir kaydırma (shift) dizisi üretir.
        """
        shifts = []
        current_val = self.base_constant
        
        for i in range(length):
            # Sürekli çarpım ve dönüşüm mantığı
            current_val = (current_val * 1.618033) % 997 # Altın oran ve modül ile akışı çeşitlendiriyoruz
            shift = int(current_val + i) % 256
            shifts.append(shift)
            
        return shifts

    def encrypt(self, plaintext: str, copy_to_clipboard: bool = True) -> str:
        """
        Düz metni formül tabanlı akış şifrelemesi ile şifreler.
        """
        shifts = self._generate_stream(len(plaintext))
        encrypted_chars = []
        
        for char, shift in zip(plaintext, shifts):
            # Karakterin ASCII değerine formülden gelen dinamik kaydırmayı ekle
            encrypted_char = chr((ord(char) + shift) % 256)
            encrypted_chars.append(encrypted_char)
            
        ciphertext = "".join(encrypted_chars)
        
        if copy_to_clipboard and CLIPBOARD_AVAILABLE:
            pyperclip.copy(ciphertext)
            print("[Bilgi] Formül şifreli metin panoya kopyalandı! (Ctrl+V yapabilirsiniz)")
            
        return ciphertext

    def decrypt(self, ciphertext: str) -> str:
        """
        Şifrelenmiş metni aynı formül akışını kullanarak çözer.
        """
        shifts = self._generate_stream(len(ciphertext))
        decrypted_chars = []
        
        for char, shift in zip(ciphertext, shifts):
            # Şifreleme adımlarını tersine çevir
            decrypted_char = chr((ord(char) - shift) % 256)
            decrypted_chars.append(decrypted_char)
            
        return "".join(decrypted_chars)

# --- TEST ETME VAKTİ ---
if __name__ == "__main__":
    app = FormulaStreamEncrypter()
    
    girdi = "AAAAA"
    print(f"Orijinal Metin: {girdi}")
    
    # Şifrele ve panoya kopyala
    sifreli_hali = app.encrypt(girdi, copy_to_clipboard=True)
    print(f"Şifreli Çıktı: {repr(sifreli_hali)}")
    
    # Geri Çöz
    cozulmus_hali = app.decrypt(sifreli_hali)
    print(f"Çözülen Metin: {cozulmus_hali}")
