import streamlit as st
import google.generativeai as genai
from datetime import datetime
from PIL import Image

# 1. SETUP & LOGO
st.set_page_config(page_title="Zyntra AI", page_icon="logo.png", layout="centered")

try:
    img = Image.open("logo.png")
    st.image(img, width=150)
except:
    st.title("🧘 Zyntra AI")

# 2. GOOGLE AI CONFIG
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")
    st.stop()

model = genai.GenerativeModel("gemini-1.5-flash")

# 3. ACCESS CONTROL
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

is_blocked = not st.session_state.is_paid and st.session_state.usage_count >= 3

# 4. PAYMENT SCREEN (Only shows when blocked)
if is_blocked:
    st.warning("🔒 Free Limit Reached")
    st.subheader("Upgrade to Zyntra Pro")
    st.write("You've used your 3 free credits. Pay to unlock unlimited support.")
    st.info("UPI ID: **your-name@airtel**") # <--- Change this to your real ID!
    
    access_code = st.text_input("Enter Access Code:", type="password")
    if st.button("Activate"):
        if access_code == "ZEN2026":
            st.session_state.is_paid = True
            st.rerun()
        else:
            st.error("Invalid Code.")
    st.stop() # This STOPS the app only if blocked

# 5. CHAT INTERFACE (This will now show for everyone else)
if not st.session_state.is_paid:
    st.caption(f"Free Plan: {3 - st.session_state.usage_count} free questions remaining")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

# THE CHAT BOX
if prompt := st.chat_input("Ask Zyntra about your robotics project..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = model.generate_content(prompt)
    st.chat_message("assistant").write(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    if not st.session_state.is_paid:
        st.session_state.usage_count += 1
        st.rerun()

st.divider()
st.caption(f"© {datetime.now().year} Zyntra Labs")
