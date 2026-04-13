import streamlit as st
import google.generativeai as genai
from datetime import datetime
from PIL import Image # This is new!

# 1. SETUP & LOGO
# This tells the browser to look for a file named "logo.png"
st.set_page_config(page_title="Zyntra AI", page_icon="logo.png", layout="centered")

# This puts the logo at the top of your site
try:
    img = Image.open("logo.png")
    st.image(img, width=200) 
except:
    st.title("🧘 Zyntra") # This shows if you haven't uploaded logo.png yet

# 1. SETUP
st.set_page_config(page_title="Zyntra AI", page_icon="🧘")

# 2. GOOGLE AI CONFIG
# Make sure you added GOOGLE_API_KEY in Streamlit 'Secrets'
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please add your GOOGLE_API_KEY in Streamlit Settings > Secrets.")
    st.stop()

# 3. ACCESS CONTROL
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

# --- FRONT PAGE ---
if not st.session_state.is_paid:
    st.title("🧘 Welcome to Zyntra")
    st.write("The smartest AI for ESP32-CAM and Robotics.")
    st.divider()
    
    st.subheader("Unlock Zyntra Pro")
    st.write("Pay via UPI to get your access code:")
    st.info("UPI ID: your-phone-number@airtel") # <--- PUT YOUR REAL ID HERE
    
    st.write("Price: ₹99 (3 Months) / ₹199 (Monthly Max)")
    
    access_code = st.text_input("Enter your secret Access Code:", type="password")
    if st.button("Activate"):
        if access_code == "ZEN2026": # This is the code you give to customers
            st.session_state.is_paid = True
            st.success("Access Granted!")
            st.rerun()
        else:
            st.error("Incorrect code. Please pay to receive the code.")
    st.stop()

# --- CHAT INTERFACE ---
st.title("🧘 Zyntra Active")
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Ask about your Arduino or ESP32 project..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = model.generate_content(prompt)
    st.chat_message("assistant").write(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

st.divider()
st.caption(f"© {datetime.now().year} Zyntra Labs. SGI Notice: Powered by AI.")
