import streamlit as st
import requests
import json

# 1. PAGE CONFIG
st.set_page_config(page_title="Zyntra", layout="wide")

# 2. SESSION STATE
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. FAST CACHED MODEL FINDER (Filters out deprecated 2.5-flash)
@st.cache_data(ttl=3600)
def get_best_model(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url, timeout=5).json()
        if "models" in res:
            for m in res["models"]:
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                
                # Exclude deprecated model names and embeddings
                if "generateContent" in methods and "embedding" not in name:
                    if name != "models/gemini-2.5-flash":
                        return name
    except Exception:
        pass
    return "models/gemini-1.5-flash-8b"

# 4. TOP RIGHT BUTTONS
c1, c2, c3 = st.columns([8, 1, 1])

with c2: 
    if st.button("Sign in"):
        st.session_state.show_modal = "signin"

with c3: 
    if st.button("Login"):
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

# 5. HERO HEADING
st.markdown("<h1 style='text-align: center; margin-top: 30px;'>Where should we start ?</h1>", unsafe_allow_html=True)

# 6. DISPLAY PREVIOUS CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. CHAT INPUT & EXECUTION
prompt = st.chat_input("Ask anything")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                active_model = get_best_model(api_key)
                
                url = f"https://generativelanguage.googleapis.com/v1beta/{active_model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"You are Zyntra AI, a fast, clean, and helpful AI assistant. Answer directly without showing your reasoning thoughts:\n\n{prompt}"}]
                    }]
                }
                
                res = requests.post(url, json=payload, timeout=10).json()
                
                if "candidates" in res:
                    reply = res["candidates"][0]["content"]["parts"][0]["text"]
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    err_msg = res.get("error", {}).get("message", "API error occurred.")
                    st.error(f"Error: {err_msg}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
