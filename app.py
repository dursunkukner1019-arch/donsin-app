import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class SecureEncrypter:
    def __init__(self, key: bytes = None):
        self.key = key if key else AESGCM.generate_key(bit_length=256)

    def encrypt(self, plaintext: str, copy_to_clipboard: bool = True) -> dict:
        """
        Düz metni AES-GCM ile şifreler ve isteğe bağlı olarak panoya kopyalar.
        """
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        
        # Hex formatına çeviriyoruz ki kolayca saklanabilsin
        encrypted_hex = ciphertext.hex()
        
        # Panoya kopyalama işlemi
        if copy_to_clipboard and CLIPBOARD_AVAILABLE:
            pyperclip.copy(encrypted_hex)
            print("[Bilgi] Şifreli metin panoya kopyalandı! (Ctrl+V yapabilirsiniz)")
        elif copy_to_clipboard and not CLIPBOARD_AVAILABLE:
            print("[Uyarı] 'pyperclip' kütüphanesi bulunamadı. Panoya kopyalanamadı.")
            print("Yüklemek için: pip install pyperclip")

        return {
            "nonce": nonce.hex(),
            "ciphertext": encrypted_hex,
            "key": self.key.hex()
        }

    def decrypt(self, nonce_hex: str, ciphertext_hex: str, key_hex: str) -> str:
        """
        Şifrelenmiş veriyi güvenli bir şekilde çözer.
        """
        aesgcm = AESGCM(bytes.fromhex(key_hex))
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        
        try:
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted_data.decode('utf-8')
        except Exception:
            raise ValueError("Şifre çözme başarısız! Veri kurcalanmış veya anahtar yanlış.")

# --- TEST ETME VAKTİ ---
if __name__ == "__main__":
    encrypter = SecureEncrypter()
    
    girdi = "AAAAA"
    print(f"Düz Metin: {girdi}")
    
    # Şifrele ve panoya kopyala
    sonuc = encrypter.encrypt(girdi, copy_to_clipboard=True)
    print(f"Şifreli Çıktı: {sonuc['ciphertext']}")
    
    # Çözüm Testi
    cozulmus = encrypter.decrypt(sonuc['nonce'], sonuc['ciphertext'], sonuc['key'])
    print(f"Çözülen Metin: {cozulmus}")
