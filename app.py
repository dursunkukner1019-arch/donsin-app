import streamlit as st
import pandas as pd

class DonSinSecEngine:
    def __init__(self):
        self.seed = int("411522633744855967078189300")
        self.multiplier = 19

    def generate_trace(self, length):
        keys, trace_data = [], []
        current = self.seed
        for step in range(1, length + 1):
            current = current * self.multiplier
            current_str = str(current)
            idx = current_str.find("4115")
            offset = idx if idx != -1 else (len(current_str) % 256)
            keys.append(offset)
            trace_data.append({
                "Adım": step,
                "Basamak Sayısı": len(current_str),
                "4115 İndeks Konumu": idx if idx != -1 else "Modüler Kayma",
                "Şifre Anahtarı": offset
            })
        return keys, trace_data

    def encrypt(self, text):
        raw_bytes = text.encode("utf-8")
        keys, trace = self.generate_trace(len(raw_bytes))
        encrypted_bytes = [b ^ (key % 256) for b, key in zip(raw_bytes, keys)]
        return bytes(encrypted_bytes).hex(), trace, len(raw_bytes)

    def decrypt(self, hex_str):
        try:
            encrypted_bytes = bytes.fromhex(hex_str)
            keys, _ = self.generate_trace(len(encrypted_bytes))
            decrypted_bytes = [b ^ (k % 256) for b, k in zip(encrypted_bytes, keys)]
            return bytes(decrypted_bytes).decode("utf-8")
        except Exception as e:
            return None

st.set_page_config(page_title="DÖN-SİN Security", page_icon="🔐")
st.title("🔐 DÖN-SİN Kriptografik Güvenlik Platformu")

engine = DonSinSecEngine()
tab1, tab2 = st.tabs(["🔒 Şifrele", "🔓 Şifre Çöz"])

with tab1:
    user_input = st.text_input("Şifrelenecek Mesaj:", "DÖN-SİN Başarıyla Çalışıyor!")
    if st.button("Şifrele"):
        hex_output, trace, byte_len = engine.encrypt(user_input)
        st.success("Başarıyla Şifrelendi!")
        st.write("**Şifreli Kod (Hex):**")
        st.code(hex_output)
        st.info(f"💡 Şifreyi çözerken uzunluk girmeniz gerekmez (Bayt Boyutu: {byte_len})")
        st.dataframe(pd.DataFrame(trace))

with tab2:
    hex_input = st.text_input("Şifreli Kodu Girin:")
    if st.button("Şifreyi Çöz"):
        if hex_input:
            result = engine.decrypt(hex_input.strip())
            if result:
                st.success(f"Çözülen Mesaj: {result}")
            else:
                st.error("Hatalı kod veya geçersiz veri!")
        else:
            st.warning("Lütfen şifreli bir kod girin.")
