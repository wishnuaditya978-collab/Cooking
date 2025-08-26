import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Ahli Resep Gemini", page_icon="👩‍🍳")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# Mengambil API Key dari Streamlit Secrets atau environment variable
# Ini adalah cara paling aman untuk menyimpan API Key di Streamlit Cloud.
# Nama secret harus 'GOOGLE_API_KEY'
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Pastikan API Key ada
if not API_KEY:
    st.error("API Key Gemini tidak ditemukan. Harap atur 'GOOGLE_API_KEY' di Streamlit Secrets.")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli memasak. Beri resep-resep yang terbaru dan enak. Jawaban singkat dan faktual. Tolak pertanyaan non-memasak."]
    },
    {
        "role": "model",
        "parts": ["Halo! Saya siap membantu Anda menemukan resep-resep lezat. Resep apa yang ingin Anda ketahui?"]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

# Judul dan deskripsi aplikasi
st.title("👨‍🍳 Chatbot Ahli Resep")
st.write("Tanyakan resep apa saja, saya akan berikan yang terbaik. Saya hanya bisa membahas resep, ya!")

# Inisialisasi Gemini API
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi model: {e}")
    st.stop()

# Inisialisasi riwayat chat di session state Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT

# Tampilkan pesan dari riwayat chat
for message in st.session_state.chat_history:
    if message["role"] != "system":  # Jangan tampilkan instruksi sistem
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])

# Tangani input pengguna
if user_input := st.chat_input("Tanyakan resep favorit Anda..."):
    # Tampilkan pesan pengguna di chat
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Tambahkan pesan pengguna ke riwayat chat
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})

    # Mulai sesi chat dengan riwayat yang ada
    chat = model.start_chat(history=st.session_state.chat_history)

    # Kirim pesan ke Gemini dan dapatkan respons
    try:
        response = chat.send_message(user_input, request_options={"timeout": 60})
        gemini_response = response.text
    except Exception as e:
        gemini_response = f"Maaf, terjadi kesalahan saat menghubungi Gemini. Detail: {e}"

    # Tampilkan respons Gemini di chat
    with st.chat_message("model"):
        st.markdown(gemini_response)

    # Tambahkan respons Gemini ke riwayat chat
    st.session_state.chat_history.append({"role": "model", "parts": [gemini_response]})
    
