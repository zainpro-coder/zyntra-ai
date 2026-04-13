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
    st.title("Zyntra") # This shows if you haven't uploaded logo.png yet

# 1. SETUP
st.set_page_config(page_title="Zyntra AI", page_icon="[/..\]")

# 2. GOOGLE AI CONFIG
# Make sure you added GOOGLE_API_KEY in Streamlit 'Secrets'
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please add your GOOGLE_API_KEY in Streamlit Settings > Secrets.")
    st.stop()

# 3. ACCESS CONTROL
# --- 3. ACCESS CONTROL (Free vs Paid) ---
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

# This determines if the user sees the chat or the payment screen
is_blocked = not st.session_state.is_paid and st.session_state.usage_count >= 3

# --- 4. FRONT PAGE & PAYMENT SECTION ---
# This block only shows up if they haven't paid AND they used their 3 free messages
if is_blocked:
    st.warning("🔒 Free Limit Reached")
    st.title("Welcome to Zyntra Pro")
    st.write("You've used your 3 free credits. To continue with unlimited robotics support, please upgrade.")
    
    # Pricing Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Zyntra Pro", "₹99 / 3 Mo")
    with col2:
        st.metric("Zyntra Max", "₹199 / Mo")

    st.divider()
    st.info("Scan or Pay via UPI: **yourname@airtel**") # <--- Replace with your ID
    
    access_code = st.text_input("Enter your secret Access Code:", type="password")
    if st.button("Activate Unlimited Access"):
        if access_code == "ZEN2026": # This is your password
            st.session_state.is_paid = True
            st.success("Access Granted! Enjoy Zyntra Pro.")
            st.rerun()
        else:
            st.error("Invalid Code. Please pay to receive your code.")
    
  

# --- 5. CHAT INTERFACE ---
st.title(" Zyntra AI")

# Show the "Free Meter" only for people who haven't paid
if not st.session_state.is_paid:
    remaining = 3 - st.session_state.usage_count
    st.caption(f"Free Plan: {remaining} free questions remaining")
