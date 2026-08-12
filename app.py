# --- FUNCTIONAL SIGN IN & LOGIN MODALS ---

@st.dialog("Sign In to Zyntra")
def show_signin():
    st.write("Welcome back! Enter your details below.")
    email = st.text_input("Email", key="signin_email")
    password = st.text_input("Password", type="password", key="signin_pass")
    
    if st.button("Sign In"):
        if email and password:
            st.success(f"Logged in as {email}")
            st.session_state.is_logged_in = True
            st.rerun()
        else:
            st.error("Please enter both email and password.")

@st.dialog("Create a Zyntra Account")
def show_login():
    st.write("Create an account to save your AI chats.")
    new_user = st.text_input("Username", key="new_user")
    new_email = st.text_input("Email", key="new_email")
    new_pass = st.text_input("Password", type="password", key="new_pass")
    
    if st.button("Create Account"):
        if new_user and new_email and new_pass:
            st.success("Account created successfully!")
            st.session_state.is_logged_in = True
            st.rerun()
        else:
            st.error("Please fill in all fields.")

# 2. TOP RIGHT BUTTONS & MODAL TRIGGER
c1, c2, c3 = st.columns([8, 1, 1])

with c2: 
    if st.button("Sign in"):
        show_signin()

with c3: 
    if st.button("login"):
        show_login()
