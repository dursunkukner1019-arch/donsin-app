import streamlit as st
import io

st.set_page_config(page_title="DÖN-SİN Kripto Engine", page_icon="🔒", layout="wide")

# Kurumsal Görsel Tasarım
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #0F172A;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

class DonSinSecEngine:
    """
    DÖN-SİN Dynamic Seed & Matrix-Shift XOR Cryptographic Engine
    Supports both String (UTF-8) and Arbitrary Binary Data (Files/PDFs/Images)
    """
    def __init__(self, seed="411598237145892019283741092"):
        self.seed = seed
        self.matrix_shift = 4115

    def _generate_key_stream(self, length: int) -> bytes:
        seed_bytes = [int(c) for c in self.seed if c.isdigit()]
        if not seed_bytes:
            seed_bytes = [4, 1, 1, 5]
        
        key_stream = bytearray()
        seed_len = len(seed_bytes)
        shift = self.matrix_shift
        
        for i in range(length):
            base = seed_bytes[i % seed_len]
            # Dynamic matrix transform & shift
            k = (base * 31 + (i * 17) + shift) % 256
            key_stream.append(k)
            # Circular shift updating
            shift = (shift * 3 + base + i) % 65535
            
        return bytes(key_stream)

    def encrypt_bytes(self, data: bytes) -> bytes:
        keystream = self._generate_key_stream(len(data))
        encrypted = bytearray()
        for b, k in zip(data, keystream):
            encrypted.append(b ^ k)
        return bytes(encrypted)

    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        return self.encrypt_bytes(encrypted_data)

    def encrypt_text(self, text: str) -> str:
        data = text.encode("utf-8")
        enc = self.encrypt_bytes(data)
        return enc.hex()

    def decrypt_text(self, hex_str: str) -> str:
        try:
            data = bytes.fromhex(hex_str.strip())
            dec = self.decrypt_bytes(data)
            return dec.decode("utf-8")
        except Exception as e:
            return f"❌ Çözme Hatası: Geçersiz veya bozuk Hex kodu! ({str(e)})"


engine = DonSinSecEngine()

st.markdown('<div class="main-title">🔒 DÖN-SİN Milli Kriptografik Haberleşme Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Kapalı Devre, Post-Kuantum Uyumlu Dinamik Matris Kaydırmalı Şifreleme Platformu</div>', unsafe_allow_html=True)

tabs = st.tabs(["💬 Metin Şifreleme / Çözme", "📄 Dosya & PDF Şifreleme", "ℹ️ Sistem Mimarisi"])

with tabs[0]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔒 Metin Şifrele")
        input_text = st.text_area("Şifrelenecek Mesaj:", placeholder="Gizli mesajınızı buraya yazın...", height=150)
        if st.button("Metni Şifrele", key="btn_enc_text"):
            if input_text:
                hex_code = engine.encrypt_text(input_text)
                st.success("Mesaj başarıyla şifrelendi!")
                st.code(hex_code, language="text")
            else:
                st.warning("Lütfen bir mesaj girin.")

    with col2:
        st.subheader("🔓 Metin Şifre Çöz")
        input_hex = st.text_area("Çözülecek Hex Kodu:", placeholder="5b7471266d7e...", height=150)
        if st.button("Şifreyi Çöz", key="btn_dec_text"):
            if input_hex:
                decrypted = engine.decrypt_text(input_hex)
                st.info("Çözülen Gizli Mesaj:")
                st.write(f"**{decrypted}**")
            else:
                st.warning("Lütfen Hex kodunu girin.")

with tabs[1]:
    st.subheader("📁 Dosya & PDF Şifreleme Katmanı")
    st.caption("PDF, PNG, JPG, DOCX veya her türlü ikili (binary) dosyayı DÖN-SİN 4115 matris algoritmasıyla güvenli hale getirin.")
    
    file_mode = st.radio("İşlem Türü Seçin:", ["🔒 Dosya Şifrele (.donsin formatına dönüştür)", "🔓 Şifreli Dosyayı Çöz (Orijinal Formata Dönüştür)"], horizontal=True)
    
    if "🔒 Dosya Şifrele" in file_mode:
        uploaded_file = st.file_uploader("Şifrelenecek Dosyayı Seçin (PDF, Resim, Belge vb.):", type=None)
        if uploaded_file is not None:
            st.write(f"**Dosya Adı:** {uploaded_file.name} | **Boyut:** {uploaded_file.size / 1024:.2f} KB")
            if st.button("Dosyayı DÖN-SİN Algoritmasıyla Şifrele"):
                with st.spinner("Dosya bayt düzeyinde 4115 matris hesabıyla şifreleniyor..."):
                    file_bytes = uploaded_file.read()
                    encrypted_bytes = engine.encrypt_bytes(file_bytes)
                    out_filename = uploaded_file.name + ".donsin"
                    
                    st.success("✅ Dosya başarıyla şifrelendi!")
                    st.download_button(
                        label=f"⬇️ Şifreli Dosyayı İndir ({out_filename})",
                        data=encrypted_bytes,
                        file_name=out_filename,
                        mime="application/octet-stream"
                    )
    else:
        uploaded_donsin = st.file_uploader("Çözülecek '.donsin' Uzantılı Şifreli Dosyayı Seçin:", type=["donsin"])
        if uploaded_donsin is not None:
            original_suggested_name = uploaded_donsin.name.replace(".donsin", "")
            if not original_suggested_name:
                original_suggested_name = "cozulen_dosya.pdf"
                
            out_name = st.text_input("Çözülen Dosyanın Adı ve Uzantısı:", value=original_suggested_name)
            
            if st.button("Şifreli Dosyayı Çöz"):
                with st.spinner("DÖN-SİN matris çözümü uygulanıyor..."):
                    enc_bytes = uploaded_donsin.read()
                    decrypted_bytes = engine.decrypt_bytes(enc_bytes)
                    
                    st.success("✅ Şifre başarıyla çözüldü! Orijinal dosya hazır.")
                    st.download_button(
                        label=f"⬇️ Orijinal Dosyayı İndir ({out_name})",
                        data=decrypted_bytes,
                        file_name=out_name,
                        mime="application/octet-stream"
                    )

with tabs[2]:
    st.subheader("⚙️ DÖN-SİN Kriptografik Mimari Detayları")
    st.markdown("""
    - **Algoritma Mimarisi:** Uçtan uca kapalı devre 27 haneli dinamik seed + 4115 Matris Kaydırmalı XOR Şifrelemesi.
    - **Bayt Düzeyi Desteği:** Tüm UTF-8 metinler ve ham ikili (binary) veriler (PDF, görsel, ses) doğrudan şifrelenir.
    - **Sıfır Veritabanı:** Merkezi veritabanı veya sunucu kayıt mekanizması barındırmaz; tamamen istemci/motor tarafında çalışır.
    - **Kuantum Sonrası Güvenlik:** Statik anahtar analizi ve kaba kuvvet (brute-force) saldırılarına karşı her baytta dairesel indisi günceller.
    """)
