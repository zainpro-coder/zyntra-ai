import streamlit as st
import requests
import json

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="Zyntra", layout="wide")

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
        margin-top: 50px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE FOR MODALS & CHAT HISTORY
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. TOP RIGHT BUTTONS
c1, c2, c3 = st.columns([8, 1, 1])

with c2: 
    if st.button("Sign in"):
        st.session_state.show_modal = "signin"

with c3: 
    if st.button("login"):
        st.session_state.show_modal = "login"

# --- MODAL POPUPS ---
if st.session_state.show_modal == "signin":
    with st.expander("🔑 Sign In to Zyntra", expanded=True):
        st.write("Welcome back! Enter your credentials:")
        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_pass")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Submit Sign In"):
                if email and password:
                    st.success(f"Logged in as {email}")
                    st.session_state.show_modal = None
                    st.rerun()
                else:
                    st.error("Please fill in both fields.")
        with col_b:
            if st.button("Close"):
                st.session_state.show_modal = None
                st.rerun()

elif st.session_state.show_modal == "login":
    with st.expander("📝 Create a Zyntra Account", expanded=True):
        st.write("Register for a new account:")
        new_user = st.text_input("Username", key="new_user")
        new_email = st.text_input("Email", key="new_email")
        new_pass = st.text_input("Password", type="password", key="new_pass")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Register Account"):
                if new_user and new_email and new_pass:
                    st.success("Account created successfully!")
                    st.session_state.show_modal = None
                    st.rerun()
                else:
                    st.error("Please fill in all fields.")
        with col_b:
            if st.button("Close"):
                st.session_state.show_modal = None
                st.rerun()

# 4. HERO HEADING
st.markdown('<p class="center-text">Where should we start ?</p>', unsafe_allow_html=True)

# 5. CHAT INPUT & UNLIMITED RESPONSE LOOP
prompt = st.chat_input("Ask anything")

if prompt:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        
        # Discover clean models from your key
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        list_res = requests.get(url).json()
        
        valid_models = []
        if "models" in list_res:
            for m in list_res["models"]:
                name = m["name"].replace("models/", "")
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    if "gemma" not in name.lower() and "2.5-flash" not in name:
                        valid_models.append(name)
        
        if not valid_models:
            valid_models = ["gemini-1.5-flash", "gemini-pro"]

        reply = None
        for model_name in valid_models:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"You are Zyntra AI, a helpful, fast, and polite AI assistant. Answer directly and cleanly without printing internal reasoning:\n\nUser: {prompt}"}]}]
            }
            res = requests.post(endpoint, json=payload).json()
            if "candidates" in res:
                reply = res["candidates"][0]["content"]["parts"][0]["text"]
                break
        
        if reply:
            st.markdown(f"**Zyntra:**\n\n{reply}")
        else:
            st.error("Failed to generate response. Please try again.")
            
    except Exception as e:
        st.error(f"Error: {e}")
