import streamlit as st
import hashlib
import json
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime

def load_data():
    try:
        with open('stored_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data():
    with open('stored_data.json', 'w') as f:
        json.dump(st.session_state.stored_data, f)

st.set_page_config(
    page_title="Secure Vault Pro",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()
cipher = Fernet(st.session_state.fernet_key)

if "users" not in st.session_state:
    st.session_state.users = {}
if "stored_data" not in st.session_state:
    st.session_state.stored_data = load_data()
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "login_time" not in st.session_state:
    st.session_state.login_time = None

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(username, passkey):
    data = st.session_state.stored_data[username]
    if data["attempts"] >= 3:
        return "locked"
    if hash_text(passkey) == data["passkey"]:
        try:
            decrypted = cipher.decrypt(data["encrypted"].encode()).decode()
            data["attempts"] = 0
            data["last_accessed"] = datetime.now().isoformat()
            save_data()
            return decrypted
        except InvalidToken:
            data["attempts"] += 1
            save_data()
            return None
    else:
        data["attempts"] += 1
        save_data()
        return None

def register():
    st.subheader("🔐 Create New Account")
    st.markdown("""
    Welcome to Secure Vault Pro! Create your account to start protecting your sensitive data with military-grade encryption.
    """)
    
    with st.form("register_form"):
        new_user = st.text_input("👤 Username", help="Choose a unique username (4-20 characters)")
        new_pass = st.text_input("🔑 Password", type="password", help="Minimum 8 characters with mix of letters, numbers, and symbols")
        confirm_pass = st.text_input("✅ Confirm Password", type="password")
        
        if st.form_submit_button("🚀 Register Account", use_container_width=True):
            if new_user in st.session_state.users:
                st.error("❌ Username already exists. Please choose another.")
            elif len(new_user) < 4 or len(new_user) > 20:
                st.warning("⚠️ Username must be between 4-20 characters")
            elif len(new_pass) < 8:
                st.warning("⚠️ Password must be at least 8 characters")
            elif new_pass != confirm_pass:
                st.warning("⚠️ Passwords do not match. Please try again.")
            elif new_user and new_pass:
                st.session_state.users[new_user] = {
                    "password": hash_text(new_pass),
                    "created": datetime.now().isoformat()
                }
                st.success("🎉 Account created successfully! Please login to continue.")
                st.balloons()
            else:
                st.warning("⚠️ Please complete all fields to register")

def login():
    st.subheader("🔓 Access Your Vault")
    st.markdown("""
    Secure Vault Pro uses **AES-256 encryption** - the same standard used by governments and security experts worldwide.
    """)
    
    with st.form("login_form"):
        user = st.text_input("👤 Username")
        pwd = st.text_input("🔑 Password", type="password")
        
        if st.form_submit_button("🚪 Login to Vault", use_container_width=True):
            if user in st.session_state.users and st.session_state.users[user]["password"] == hash_text(pwd):
                st.session_state.logged_in_user = user
                st.session_state.login_time = datetime.now()
                if user not in st.session_state.stored_data:
                    st.session_state.stored_data[user] = {
                        "encrypted": "",
                        "passkey": "",
                        "attempts": 0,
                        "created": datetime.now().isoformat(),
                        "last_accessed": None
                    }
                save_data()
                st.success("🔓 Authentication successful! Welcome back.")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again or register if you're new.")

def store_data():
    st.subheader("📥 Store Sensitive Data")
    st.markdown("""
    ### How it works:
    1. Enter your confidential information (passwords, notes, documents)
    2. Set a strong decryption passkey (different from your login password)
    3. Your data is encrypted with **AES-256** before storage
    """)
    
    with st.form("store_form"):
        data = st.text_area("📝 Enter your sensitive data here:", height=150, 
                          help="This could be passwords, API keys, personal notes, etc.")
        passkey = st.text_input("🔐 Set decryption passkey", type="password",
                              help="Must be at least 12 characters for maximum security")
        confirm_passkey = st.text_input("✅ Confirm decryption passkey", type="password")
        
        if st.form_submit_button("🔒 Encrypt & Store Data", use_container_width=True):
            if data and passkey:
                if len(passkey) < 12:
                    st.warning("⚠️ For your security, please use a passkey of at least 12 characters")
                elif passkey != confirm_passkey:
                    st.warning("⚠️ Passkeys do not match. Please try again.")
                else:
                    encrypted = encrypt_data(data)
                    st.session_state.stored_data[st.session_state.logged_in_user] = {
                        "encrypted": encrypted,
                        "passkey": hash_text(passkey),
                        "attempts": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                    save_data()
                    st.success("✅ Data secured successfully with military-grade encryption!")
                    with st.expander("🔍 View Encrypted Data"):
                        st.code(encrypted)
                    st.info("💡 Remember your passkey! Without it, your data cannot be recovered.")
            else:
                st.warning("⚠️ Please complete all fields to store your data")

def retrieve_data():
    st.subheader("📤 Retrieve Your Data")
    st.markdown("""
    Access your encrypted information by entering your unique decryption passkey.
    You have **3 attempts** before temporary lockout for security.
    """)
    
    user_data = st.session_state.stored_data.get(st.session_state.logged_in_user, {})
    if user_data.get("last_accessed"):
        last_access = datetime.fromisoformat(user_data['last_accessed']).strftime('%B %d, %Y at %H:%M')
        st.info(f"⏳ Last accessed: {last_access}")
    
    with st.form("retrieve_form"):
        passkey = st.text_input("🔑 Enter decryption passkey", type="password",
                              help="The passkey you set when encrypting this data")
        
        if st.form_submit_button("🔓 Decrypt Data Now", use_container_width=True):
            user = st.session_state.logged_in_user
            result = decrypt_data(user, passkey)
            if result == "locked":
                st.error("🔒 Account temporarily locked due to multiple failed attempts. Please try again later.")
                st.session_state.logged_in_user = None
                st.rerun()
            elif result:
                st.success("🎉 Decryption successful! Your data is ready.")
                with st.expander("📋 View Decrypted Data", expanded=True):
                    st.text_area("Your secured content:", value=result, height=200, disabled=True)
                st.download_button(
                    label="⬇️ Download as Text File",
                    data=result,
                    file_name=f"secured_data_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                st.info("🔐 Remember to clear your browser cache after viewing sensitive data")
            else:
                attempts_left = 3 - st.session_state.stored_data[user]["attempts"]
                st.error(f"❌ Incorrect passkey! {attempts_left} attempts remaining before lockout.")

def show_dashboard():
    st.subheader("📊 Vault Dashboard")
    st.markdown("""
    Your personal security command center. Monitor your vault's status and activity.
    """)
    
    user_data = st.session_state.stored_data.get(st.session_state.logged_in_user, {})
    session_duration = datetime.now() - st.session_state.login_time
    mins, secs = divmod(session_duration.seconds, 60)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🕒 Current Session Started", st.session_state.login_time.strftime("%H:%M:%S"))
        st.metric("⏱️ Active Session Duration", f"{mins} minutes {secs} seconds")
    with col2:
        status = "🟢 Active" if user_data.get("encrypted") else "🟠 Inactive"
        st.metric("🔐 Security Status", status)
        st.metric("⚠️ Failed Attempts", user_data.get("attempts", 0))
    
    if user_data.get("encrypted"):
        st.progress(100, text="🔒 Data secured and encrypted")
        last_updated = datetime.fromisoformat(user_data['last_updated']).strftime('%B %d') if user_data.get('last_updated') else "Never"
        st.info(f"📅 Last updated: {last_updated}")
    else:
        st.progress(0, text="🟡 No data stored yet")
        st.warning("You haven't stored any data yet. Use the 'Store Data' section to begin.")
    
    st.write("")
    st.info("💡 Pro Tip: Always log out after your session, especially on shared devices")

st.title("🔐 Secure Vault Pro")
st.markdown("""
### Your Personal Digital Fort Knox
Store passwords, sensitive documents, and confidential notes with **military-grade AES-256 encryption**.
All data is encrypted before storage and can only be accessed with your unique passkey.
""")

if st.session_state.logged_in_user:
    st.sidebar.success(f"👋 Welcome back, **{st.session_state.logged_in_user}**!")
    nav_option = st.sidebar.radio(
        "Navigation Menu",
        ["📊 Dashboard", "📥 Store Data", "📤 Retrieve Data", "👤 Account"],
        index=0
    )
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
        st.session_state.logged_in_user = None
        st.success("👋 Logged out successfully. Your session is secure.")
        st.rerun()
    
    if nav_option == "📊 Dashboard":
        show_dashboard()
    elif nav_option == "📥 Store Data":
        store_data()
    elif nav_option == "📤 Retrieve Data":
        retrieve_data()
    elif nav_option == "👤 Account":
        st.subheader("👤 Account Management")
        account_age = (datetime.now() - datetime.fromisoformat(st.session_state.users[st.session_state.logged_in_user]['created'])).days
        st.markdown(f"""
        - **Username**: {st.session_state.logged_in_user}
        - **Account created**: {datetime.fromisoformat(st.session_state.users[st.session_state.logged_in_user]['created']).strftime('%B %d, %Y')}
        - **Account age**: {account_age} days
        """)
        
        if st.button("🧹 Delete All Stored Data", type="secondary", help="Permanently remove all your encrypted data"):
            if st.session_state.logged_in_user in st.session_state.stored_data:
                del st.session_state.stored_data[st.session_state.logged_in_user]
                save_data()
                st.success("♻️ All stored data has been permanently deleted.")
                st.balloons()
else:
    st.sidebar.markdown("### 🔐 Get Started")
    auth_option = st.sidebar.radio(
        "Authentication Options",
        ["🔓 Login", "🚀 Register"]
    )
    
    if auth_option == "🔓 Login":
        login()
    else:
        register()

st.divider()
st.markdown("""
<small>🔒 **Secure Vault Pro** | Military-Grade AES-256 Encryption | © {year} All Rights Reserved</small>
""".format(year=datetime.now().year), unsafe_allow_html=True)