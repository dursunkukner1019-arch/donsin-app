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
        keys, trace = self.generate_trace(len(text))
        encrypted_bytes = [ord(char) ^ (key % 256) for char, key in zip(text, keys)]
        return encrypted_bytes.hex(), trace

    def decrypt(self, hex_str, length):
        encrypted_bytes = list(bytes.fromhex(hex_str))
        keys, _ = self.generate_trace(length)
        return "".join([chr(b ^ (k % 256)) for b, k in zip(encrypted_bytes, keys)])

st.set_page_config(page_title="DÖN-SİN Security", page_icon="🔐")
st.title("🔐 DÖN-SİN Kriptografik Güvenlik Platformu")

engine = DonSinSecEngine()
tab1, tab2 = st.tabs(["🔒 Şifrele", "🔓 Şifre Çöz"])

with tab1:
    user_input = st.text_input("Şifrelenecek Mesaj:", "DÖN-SİN Telefonda Canlı!")
    if st.button("Şifrele"):
        hex_output, trace = engine.encrypt(user_input)
        st.success("Başarıyla Şifrelendi!")
        st.code(hex_output)
        st.dataframe(pd.DataFrame(trace))

with tab2:
    hex_input = st.text_input("Şifreli Kodu Girin:")
    msg_len = st.number_input("Karakter Uzunluğu:", min_value=1, value=23)
    if st.button("Şifreyi Çöz"):
        try:
            st.info(f"Çözülen Mesaj: {engine.decrypt(hex_input, msg_len)}")
        except:
            st.error("Hatalı kod!")
