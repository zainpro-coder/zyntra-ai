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

# 3. TOP RIGHT BUTTONS
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

# 4. HERO HEADING
st.markdown("<h1 style='text-align: center; margin-top: 30px;'>Where should we start ?</h1>", unsafe_allow_html=True)

# 5. DISPLAY PREVIOUS CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. FAST EXECUTION WITH SYSTEM IDENTITY (CREATOR: MR. MOHAMMAD ZAIN)
prompt = st.chat_input("Ask anything")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Zyntra is thinking..."):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                
                # Fetch active models on this key
                models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                list_res = requests.get(models_url, timeout=10).json()
                
                candidate_models = []
                if "models" in list_res:
                    for m in list_res["models"]:
                        name = m.get("name", "")
                        methods = m.get("supportedGenerationMethods", [])
                        
                        if "generateContent" in methods and "embedding" not in name:
                            if "2.5-flash" not in name and "2.5-pro" not in name:
                                candidate_models.append(name)
                
                reply = None
                last_err = ""
                
                # System prompt specifying creator identity
                system_instruction = (
                    "You are Zyntra AI, an intelligent, fast, and polite AI assistant created and developed by Mr. Mohammad Zain. "
                    "Whenever asked about your creator, developer, founder, or who made you, always state clearly and respectfully that you were created by Mr. Mohammad Zain. "
                    "Always answer directly, politely, and cleanly in the user's language without showing internal reasoning steps."
                )
                
                # Try candidate models
                for target_model in candidate_models:
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"{system_instruction}\n\nUser Question: {prompt}"}]
                        }]
                    }
                    
                    res = requests.post(gen_url, json=payload, timeout=30).json()
                    
                    if "candidates" in res and len(res["candidates"]) > 0:
                        parts = res["candidates"][0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            reply = parts[0]["text"]
                            break
                    else:
                        last_err = res.get("error", {}).get("message", "")

                if reply:
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"Error: {last_err if last_err else 'Response took too long or model unavailable.'}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
