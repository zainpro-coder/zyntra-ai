import streamlit as st
import requests
import json
import base64
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
    .attachment-container {
        background-color: #1E232B;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #2D3748;
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
if "show_attachments" not in st.session_state:
    st.session_state.show_attachments = False
if "attachment_mode" not in st.session_state:
    st.session_state.attachment_mode = None

# 3. SIDEBAR (CHATGPT STYLE)
with st.sidebar:
    st.title("⚡ Zyntra AI")
    st.markdown('<p class="creator-badge">Created by <b>Mr. Mohammad Zain</b></p>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        chat_id = f"Chat {len(st.session_state.conversations) + 1}"
        st.session_state.conversations[chat_id] = []
        st.session_state.active_chat = chat_id
        st.session_state.show_attachments = False
        st.session_state.attachment_mode = None
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

# 4. USER MODAL POPUP
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
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Where should we start?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>Ask anything, brainstorm ideas, or click '+' to capture/upload.</p>", unsafe_allow_html=True)

# Display historical messages of this conversation
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"], width=300)

# 6. ATTACHMENT (+) BAR & ON-DEMAND CAMERA/FILE SELECTOR
col_plus, col_status = st.columns([1, 9])
with col_plus:
    if st.button("➕", help="Upload File or Open Camera", use_container_width=True):
        st.session_state.show_attachments = not st.session_state.show_attachments
        st.rerun()

attached_file = None

if st.session_state.show_attachments:
    with st.container():
        st.markdown("<div class='attachment-container'>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
        
        with col_btn1:
            if st.button("📁 Upload File / Image", use_container_width=True):
                st.session_state.attachment_mode = "upload"
                st.rerun()
        with col_btn2:
            if st.button("📸 Open Camera", use_container_width=True):
                st.session_state.attachment_mode = "camera"
                st.rerun()
        with col_btn3:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_attachments = False
                st.session_state.attachment_mode = None
                st.rerun()

        # Conditionally render ONLY what user clicked
        if st.session_state.attachment_mode == "upload":
            uploaded_file = st.file_uploader("Select Image or Document", type=["png", "jpg", "jpeg", "txt"], key="active_file_uploader")
            if uploaded_file:
                attached_file = uploaded_file
                st.success(f"Attached: {uploaded_file.name}")
                
        elif st.session_state.attachment_mode == "camera":
            camera_file = st.camera_input("Click 'Take Photo' when ready", key="active_camera_input")
            if camera_file:
                attached_file = camera_file
                st.success("Snapshot captured!")

        st.markdown("</div>", unsafe_allow_html=True)

# 7. INPUT & MULTIMODAL GEMINI EXECUTION
prompt = st.chat_input("Ask anything...")

if prompt:
    user_msg_entry = {"role": "user", "content": prompt}
    image_parts = []
    
    if attached_file:
        file_bytes = attached_file.getvalue()
        mime_type = attached_file.type or "image/jpeg"
        
        if mime_type.startswith("image/"):
            user_msg_entry["image"] = file_bytes
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            image_parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })
        elif mime_type == "text/plain":
            file_text = file_bytes.decode("utf-8", errors="ignore")
            prompt = f"File Content:\n```\n{file_text}\n```\n\nUser Question: {prompt}"
            user_msg_entry["content"] = prompt

    current_messages.append(user_msg_entry)
    with st.chat_message("user"):
        st.write(prompt)
        if "image" in user_msg_entry:
            st.image(user_msg_entry["image"], width=300)

    # Reset attachment panel after sending
    st.session_state.show_attachments = False
    st.session_state.attachment_mode = None

    with st.chat_message("assistant"):
        with st.spinner("Zyntra is thinking & analyzing..."):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                
                models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                list_res = requests.get(models_url, timeout=5).json()
                
                candidate_models = []
                if "models" in list_res:
                    for m in list_res["models"]:
                        name = m.get("name", "")
                        methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in methods and "embedding" not in name:
                            if "gemma" not in name.lower() and "2.5-flash" not in name and "2.5-pro" not in name:
                                candidate_models.append(name)
                
                fallback_list = candidate_models + [
                    "models/gemini-1.5-flash-8b",
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-pro"
                ]
                
                seen = set()
                final_models = [x for x in fallback_list if not (x in seen or seen.add(x))]

                system_rules = (
                    "You are Zyntra AI, an intelligent, helpful AI assistant created and developed by Mr. Mohammad Zain. "
                    "Always reply directly, politely, and cleanly in the user's language (Hindi/English/Hinglish). "
                    "When given an image, inspect it carefully and answer accurately. "
                    "Do not print internal reasoning thoughts or drafts. Output only the final response."
                )

                recent_history = current_messages[-6:]
                contents_payload = []
                for i, msg in enumerate(recent_history):
                    role_tag = "user" if msg["role"] == "user" else "model"
                    parts = [{"text": msg["content"]}]
                    
                    if i == 0 and role_tag == "user":
                        parts[0]["text"] = f"[{system_rules}]\n\n{parts[0]['text']}"
                    
                    if i == len(recent_history) - 1 and image_parts:
                        parts = image_parts + parts
                        
                    contents_payload.append({
                        "role": role_tag,
                        "parts": parts
                    })

                payload = {
                    "contents": contents_payload,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2048
                    }
                }

                reply = None
                last_err = ""
                
                for model_choice in final_models:
                    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{model_choice}:generateContent?key={api_key}"
                    try:
                        res = requests.post(gen_url, json=payload, timeout=25).json()
                        if "candidates" in res and len(res["candidates"]) > 0:
                            parts = res["candidates"][0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                raw_text = parts[0]["text"]
                                reply = re.sub(r"<thought>.*?</thought>", "", raw_text, flags=re.DOTALL).strip()
                                break
                        else:
                            last_err = res.get("error", {}).get("message", "")
                    except Exception:
                        continue
                
                if reply:
                    st.write(reply)
                    current_messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"Error: {last_err if last_err else 'Service busy. Please try again.'}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
