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

# 2. SESSION STATE LOGIC
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

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

# 5. CHAT INPUT & RESPONSE
prompt = st.chat_input("Ask anything")

if prompt:
    if not st.session_state.is_paid and st.session_state.usage_count >= 3:
        st.warning("Free limit reached. Please pay via UPI to yourname@airtel and enter your secret code.")
        code = st.text_input("Enter Access Code:", type="password")
        if code == "ZEN2026":
            st.session_state.is_paid = True
            st.success("Unlocked! Please ask your question again.")
            st.rerun()
    else:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            
            # Step 1: Discover active models directly from Google
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            list_res = requests.get(list_url).json()
            
            valid_models = []
            if "models" in list_res:
                for m in list_res["models"]:
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods:
                        # Exclude older deprecated flash variants
                        name = m["name"].replace("models/", "")
                        if "2.5-flash" not in name:
                            valid_models.append(name)
            
            # Fallback list if discovery fails
            if not valid_models:
                valid_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
            
            reply = None
            last_err = ""
            
            # Step 2: Try active endpoints
            for model_name in valid_models:
                for version in ["v1", "v1beta"]:
                    url = f"https://generativelanguage.googleapis.com/{version}/models/{model_name}:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    
                    res = requests.post(url, json=payload).json()
                    
                    if "candidates" in res:
                        reply = res["candidates"][0]["content"]["parts"][0]["text"]
                        break
                    else:
                        last_err = res.get("error", {}).get("message", "Request failed")
                if reply:
                    break
            
            if reply:
                st.markdown(f"**Zyntra:** {reply}")
                if not st.session_state.is_paid:
                    st.session_state.usage_count += 1
            else:
                st.error(f"Google API Error: {last_err}")
                
        except Exception as e:
            st.error(f"Error: {e}")
