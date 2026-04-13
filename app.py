import streamlit as st
import google.generativeai as genai

# 1. PAGE CONFIG & HIDING STREAMLIT DEFAULTS
st.set_page_config(page_title="Zyntra", layout="wide")

# CSS to make the page white and style the elements like your screenshot
# Custom CSS for the clean white look
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .center-text {
        font-family: 'Helvetica', sans-serif;
        font-size: 50px;
        font-weight: bold;
        color: black;
        text-align: center;
        margin-top: 100px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True) # Changed from 'input' to 'html'
# 2. THE UI ELEMENTS
# Top right buttons (Simulated)
col1, col2, col3 = st.columns([8, 1, 1])
with col2:
    st.button("Sign in")
with col3:
    st.button("login")

# Center Text
st.markdown('<p class="center-text">Were should we start ?</p>', unsafe_allow_input=True)

# 3. ACCESS & USAGE LOGIC (Invisible)
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

# 4. CHAT INPUT AT THE BOTTOM
# We use a container to keep it pinned at the bottom
with st.container():
    prompt = st.chat_input("Ask anything")

if prompt:
    # Logic to block after 3 questions
    if not st.session_state.is_paid and st.session_state.usage_count >= 3:
        st.warning("Limit reached. Please pay yourname@airtel and enter code.")
        code = st.text_input("Access Code", type="password")
        if code == "ZEN2026":
            st.session_state.is_paid = True
            st.rerun()
    else:
        # Connect to Gemini
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Display response
        st.write(response.text)
        
        if not st.session_state.is_paid:
            st.session_state.usage_count += 1
