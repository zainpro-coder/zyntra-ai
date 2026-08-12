import streamlit as st
import google.generativeai as genai

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

# 2. SESSION STATE FOR MODALS & USER DATA
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None  # Options: None, 'signin', 'login'
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

# --- MODAL POPUP DISPLAY LOGIC ---
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

# 5. CHAT INPUT & RESPONSE LOOP
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
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            response = model.generate_content(prompt)
            st.markdown(f"**Zyntra:** {response.text}")
            
            if not st.session_state.is_paid:
                st.session_state.usage_count += 1
                
        except Exception as e:
            st.error(f"AI Response Error: {e}")
