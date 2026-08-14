import streamlit as st
import requests
import json
import re

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="Zyntra AI", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .creator-badge {
        font-size: 13px;
        color: #9CA3AF;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE MANAGEMENT
if "conversations" not in st.session_state:
    st.session_state.conversations = {"Current Chat": []}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Current Chat"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Mohammad Zain"
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None

# 3. SIDEBAR (CHATGPT STYLE: NEW CHAT, LIBRARY, ACCOUNT)
with st.sidebar:
    st.title("⚡ Zyntra AI")
    st.markdown('<p class="creator-badge">Created by <b>Mr. Mohammad Zain</b></p>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        chat_id = f"Chat {len(st.session_state.conversations) + 1}"
        st.session_state.conversations[chat_id] = []
        st.session_state.active_chat = chat_id
        st.rerun()

    st.markdown("---")
    st.subheader("📚 Chat Library")
    for chat_name in list(st.session_state.conversations.keys()):
        col_chat, col_del = st.columns([4, 1])
        with col_chat:
            if st.button(f"💬 {chat_name}", key=f"btn_{chat_name}", use_container_width=True):
                st.session_state.active_chat = chat_name
                st.rerun()
        with col_del:
            if len(st.session_state.conversations) > 1:
                if st.button("🗑️", key=f"del_{chat_name}"):
                    del st.session_state.conversations[chat_name]
                    st.session_state.active_chat = list(st.session_state.conversations.keys())[0]
                    st.rerun()

    st.markdown("---")
    st.subheader("👤 User Account")
    st.write(f"Logged in as: **{st.session_state.user_name}**")
    if st.button("Manage Account", use_container_width=True):
        st.session_state.show_modal = "account"

# 4. MODAL POPUP
if st.session_state.show_modal == "account":
    with st.expander("👤 User Profile & Settings", expanded=True):
        new_name = st.text_input("Display Name:", value=st.session_state.user_name)
        col_save, col_close = st.columns(2)
        with col_save:
            if st.button("Save Profile"):
                st.session_state.user_name = new_name
                st.session_state.show_modal = None
                st.success("Profile Updated!")
                st.rerun()
        with col_close:
            if st.button("Close"):
                st.session_state.show_modal = None
                st.rerun()

# 5. MAIN CHAT AREA
current_messages = st.session_state.conversations[st.session_state.active_chat]

if len(current_messages) == 0:
    st.markdown("<h1 style='text-align: center; margin-top: 40px;'>Where should we start?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>Ask anything, brainstorm ideas, or just chat naturally.</p>", unsafe_allow_html=True)

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. INPUT & CLEAN CONVERSATIONAL CALL
prompt = st.chat_input("Ask anything...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Zyntra is thinking..."):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                
                # Fetch available text models
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
                
                # Format multi-turn chat history
                contents_payload = []
                for msg in current_messages:
                    role_tag = "user" if msg["role"] == "user" else "model"
                    contents_payload.append({
                        "role": role_tag,
                        "parts": [{"text": msg["content"]}]
                    })
                
                system_text = (
                    "You are Zyntra AI, a polished, witty, and concise AI assistant developed by Mr. Mohammad Zain. "
                    "CRITICAL RULES: "
                    "1. Respond directly like ChatGPT/Gemini. "
                    "2. Never output your internal thinking, scratchpad, planning steps, or drafts. "
                    "3. Keep answers crisp, clear, and to the point without unnecessary fluff. "
                    "4. If the user engages casually (e.g. 'oh', 'cool', 'okay'), reply conversationally and naturally."
                )

                payload = {
                    "system_instruction": {
                        "parts": [{"text": system_text}]
                    },
                    "contents": contents_payload,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1024
                    }
                }

                reply = None
                last_err = ""
                
                for target_model in candidate_models:
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={api_key}"
                    res = requests.post(gen_url, json=payload, timeout=25).json()
                    
                    if "candidates" in res and len(res["candidates"]) > 0:
                        parts = res["candidates"][0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_text = parts[0]["text"]
                            # Clean any leftover thinking tags or scratchpads
                            cleaned_text = re.sub(r"<thought>.*?</thought>", "", raw_text, flags=re.DOTALL).strip()
                            reply = cleaned_text if cleaned_text else raw_text
                            break
                    else:
                        last_err = res.get("error", {}).get("message", "")

                if reply:
                    st.write(reply)
                    current_messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"Error: {last_err if last_err else 'Service unavailable.'}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
