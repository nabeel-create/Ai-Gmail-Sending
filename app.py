# ============================
# 📧 AI Gmail Sender – Streamlit Cloud Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(page_title="AI Gmail Sender by Nabeel", page_icon="📧", layout="wide")

# --------------------------
# SESSION STATE FOR LOGIN
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------
# BEAUTIFUL LOGIN PAGE
# --------------------------
def login_page():
    st.markdown("""
        <style>
            body { background: #f5f7fa; }
            .login-card { background: white; padding: 40px; border-radius: 18px; box-shadow: 0 8px 20px rgba(0,0,0,0.07); width: 380px; margin: auto; margin-top: 90px; }
            .title { font-size: 26px; font-weight: 700; text-align: center; color: #333; margin-bottom: 0px; }
            .subtitle { text-align: center; color: #666; font-size: 14px; margin-bottom: 25px; }
            .stButton>button { width: 100%; background: #1a73e8; color: white; padding: 10px; border-radius: 10px; border: none; font-size: 16px; }
            .stButton>button:hover { background: #1567d5; }
            .link { text-align: center; margin-top: 15px; }
            .link a { color: #1a73e8; text-decoration: none; font-size: 14px; }
            .link a:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Sign in to Continue</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Use your Gmail and App Password</div>", unsafe_allow_html=True)

    email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    password = st.text_input("Password / App Password", type="password", placeholder="Enter your Gmail App Password")
    login_clicked = st.button("Login")

    st.markdown("""
        <div class='link'>
            Need an App Password? 
            <a href='https://myaccount.google.com/apppasswords' target='_blank'>Click here</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if login_clicked:
        if email.strip() == "" or password.strip() == "":
            st.error("Please enter both email and password.")
        else:
            st.success("Login successful!")
            st.session_state['logged_in'] = True
            st.session_state['email'] = email
            st.experimental_rerun()  # Redirect to app page

# --------------------------
# GMAIL SENDER APP
# --------------------------
def app_page():
    st.title("📧 AI Gmail Sender")
    st.caption(f"Logged in as: {st.session_state.get('email')} | Developed by Nabeel")

    # --- Load Gmail API Secrets ---
    client_id = st.secrets.get("CLIENT_ID")
    client_secret = st.secrets.get("CLIENT_SECRET")
    refresh_token = st.secrets.get("REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        st.error("Gmail API credentials are missing in Streamlit secrets!")
        return

    creds_data = {
        "token": "",
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": ["https://www.googleapis.com/auth/gmail.send"],
        "type": "authorized_user"
    }
    creds = Credentials.from_authorized_user_info(creds_data)
    service = build("gmail", "v1", credentials=creds)
    st.success("✅ Gmail API connected successfully!")

    # --- Upload Contacts ---
    st.subheader("📁 Upload Contacts")
    uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
    contacts = None
    if uploaded_file:
        contacts = pd.read_csv(uploaded_file)
        st.dataframe(contacts)

    # --- Upload Attachments ---
    st.subheader("📎 Upload Attachments (optional)")
    uploaded_attachments = st.file_uploader("Upload one or more files", type=None, accept_multiple_files=True)
    attachment_paths = []
    if uploaded_attachments:
        for f in uploaded_attachments:
            path = os.path.join(".", f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            attachment_paths.append(path)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # --- Compose Email ---
    st.subheader("📝 Compose Email")
    sender = st.text_input("Sender Gmail (authorized)", value=st.session_state.get("email"))
    subject = st.text_input("Subject")
    body = st.text_area("Body (use {{name}} for personalization)")

    # --- Email Functions ---
    def create_message(sender, to, subject, body_text, attachments=None):
        msg = MIMEMultipart()
        msg['to'] = to
        msg['from'] = sender
        msg['subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        if attachments:
            for path in attachments:
                part = MIMEBase('application', 'octet-stream')
                with open(path, 'rb') as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
                msg.attach(part)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return {'raw': raw}

    def send_message(service, user_id, message):
        try:
            sent = service.users().messages().send(userId=user_id, body=message).execute()
            return f"✅ Sent (ID: {sent['id']})"
        except Exception as e:
            return f"❌ Error: {e}"

    # --- Send Emails Button ---
    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contacts.csv first!")
        elif not sender or not subject or not body:
            st.warning("Fill sender, subject, and body fields!")
        else:
            st.info("Sending emails...")
            logs = []
            for _, row in contacts.iterrows():
                personalized = body.replace("{{name}}", row['name'])
                msg = create_message(sender, row['email'], subject, personalized, attachments=attachment_paths)
                status = send_message(service, 'me', msg)
                logs.append({'email': row['email'], 'status': status})
            st.success("✅ All emails sent successfully!")
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs)
            df_logs.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# --------------------------
# APP FLOW CONTROLLER
# --------------------------
if not st.session_state.logged_in:
    login_page()
else:
    app_page()
