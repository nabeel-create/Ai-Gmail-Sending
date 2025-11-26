# ================================================
# 📧 AI Gmail Sender – Gmail Theme (Red & White)
# Author: Nabeel
# ================================================

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")

# ------------------------
# SESSION STATE INIT
# ------------------------
for key in ["logged_in", "sender_email", "sender_password", "show_welcome"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "email" in key or "password" in key else False

# ------------------------
# CUSTOM CSS
# ------------------------
st.markdown("""
<style>
body {background-color: #f5f5f5;}
.login-box {background: white; width: 400px; padding: 40px; border-radius: 12px; margin: auto; margin-top: 100px; box-shadow: 0px 4px 15px rgba(0,0,0,0.15); border-top: 5px solid #d93025;}
.login-btn {background-color: #d93025 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 600 !important;}
section[data-testid="stSidebar"] {background-color: white; border-right: 2px solid #e3e3e3;}
.sidebar-title {font-size: 22px; font-weight: bold; color: #d93025;}
.welcome-popup {position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%); padding: 20px 30px; background: #d93025; color: white; font-size: 20px; text-align: center; border-radius: 12px; animation: fadeout 3s forwards; z-index: 9999;}
@keyframes fadeout {0% {opacity:1;} 70% {opacity:1;} 100% {opacity:0;}}
</style>
""", unsafe_allow_html=True)

# ------------------------
# HELP MENU
# ------------------------
def help_menu():
    with st.expander("⋮ How to use Gmail Login (App Password / 2FA)"):
        st.markdown("""
        **Steps to login using Gmail App Password:**
        1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
        2. Sign in with your Gmail account.
        3. Select "Mail" → "Other (Custom name)" → Generate.
        4. Copy the 16-character password into this app's password field.
        
        **Notes:**
        - If 2FA is enabled, App Password is required.
        - Normal Gmail password **will not work** if 2FA is enabled.
        - You can generate multiple app passwords for multiple devices.
        """)

# ------------------------
# LOGIN PAGE
# ------------------------
def login_page():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png", width=80)
    st.markdown("### Sign in to continue")

    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail App Password", type="password")

    st.markdown(
        "<a href='https://myaccount.google.com/apppasswords' target='_blank'>🔗 Create Gmail App Password</a>",
        unsafe_allow_html=True
    )

    help_menu()  # show three dots help

    if st.button("Login", key="login_button"):
        if not email or not password:
            st.warning("Please enter both Email and App Password")
        else:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, password)
                server.quit()

                # ✅ Update session state and return
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = password
                st.session_state.show_welcome = True

                return  # Streamlit automatically reruns and shows email sender page

            except Exception as e:
                st.error(f"Login failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# EMAIL SENDER PAGE
# ------------------------
def email_sender_page():
    if st.session_state.show_welcome:
        st.markdown("<div class='welcome-popup'>🎉 Welcome to AI Gmail Sending System!</div>", unsafe_allow_html=True)
        st.session_state.show_welcome = False

    st.sidebar.markdown("<p class='sidebar-title'>📧 AI Gmail Sender</p>", unsafe_allow_html=True)
    st.sidebar.write(f"Signed in as: **{st.session_state.sender_email}**")
    help_menu()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.sender_email = ""
        st.session_state.sender_password = ""
        return  # ✅ Single click logout shows login page immediately

    st.title("📤 Send Email")

    # Upload contacts
    contacts_file = st.file_uploader("📁 Upload Contacts CSV (name,email)", type="csv")
    contacts = pd.read_csv(contacts_file) if contacts_file else None
    if contacts is not None:
        st.dataframe(contacts)

    # Attachments
    files = st.file_uploader("📎 Upload attachments", accept_multiple_files=True)
    attachment_paths = []
    if files:
        for f in files:
            with open(f.name, "wb") as out:
                out.write(f.getbuffer())
            attachment_paths.append(f.name)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # Compose Email
    subject = st.text_input("Subject")
    body = st.text_area("Body (use {{name}} for personalization)")

    def create_message(sender, to, subject, text, attachments):
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))
        for path in attachments:
            part = MIMEBase("application", "octet-stream")
            with open(path, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
            msg.attach(part)
        return msg

    def send_email(to, msg):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(st.session_state.sender_email, st.session_state.sender_password)
            server.send_message(msg)
            server.quit()
            return "✅ Sent"
        except Exception as e:
            return f"❌ {e}"

    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contact list first!")
        elif not subject or not body:
            st.warning("Fill all fields!")
        else:
            logs = []
            for _, row in contacts.iterrows():
                text = body.replace("{{name}}", str(row["name"]))
                msg = create_message(st.session_state.sender_email, row["email"], subject, text, attachment_paths)
                status = send_email(row["email"], msg)
                logs.append({"email": row["email"], "status": status})
            df = pd.DataFrame(logs)
            st.success("All emails processed!")
            st.dataframe(df)
            df.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# ------------------------
# ROUTER
# ------------------------
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
