# ============================
# 📧 AI Gmail Sender – Elegant Version (Streamlit Cloud)
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os, base64, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender by Nabeel", page_icon="📧", layout="wide")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f9fafc 0%, #eef2f3 100%);
        color: #222;
    }
    .stApp header {visibility: hidden;}
    .big-title {
        font-size: 36px;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #0072ff, #00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 18px;
        color: #444;
    }
    .footer {
        font-size: 14px;
        color: #888;
        text-align: center;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Welcome Section ---
with st.spinner("🚀 Initializing AI Gmail Sender... Please wait..."):
    time.sleep(2)

st.markdown('<h1 class="big-title">📧 AI Gmail Sender</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Welcome to your automated Gmail sending assistant powered by AI 🤖<br>Developed with ❤️ by <b>Nabeel</b></p>', unsafe_allow_html=True)
st.divider()

# --- Load Secrets ---
try:
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    refresh_token = st.secrets["REFRESH_TOKEN"]
except KeyError:
    st.error("❌ Missing API credentials! Please add CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN in Streamlit Secrets.")
    st.stop()

# --- Gmail Authentication ---
try:
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
except Exception as e:
    st.error(f"⚠️ Gmail API connection failed: {e}")
    st.stop()

# --- Upload Contacts ---
st.subheader("📁 Upload Contact List")
uploaded_file = st.file_uploader("Upload your contacts CSV file (columns: name,email)", type="csv")
contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.dataframe(contacts, use_container_width=True)
    st.success(f"✅ {len(contacts)} contacts loaded")

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
    st.info(f"📎 {len(attachment_paths)} attachment(s) ready")

# --- Compose Email ---
st.subheader("📝 Compose Your Email")
col1, col2 = st.columns(2)
with col1:
    sender = st.text_input("Sender Gmail (authorized):")
    subject = st.text_input("Email Subject:")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("Use **{{name}}** to personalize each message.")
body = st.text_area("Email Body", height=200, placeholder="Hello {{name}},\n\nThis is an automated email from Nabeel's AI Gmail Sender...")

# --- Helper Functions ---
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

# --- Send Button ---
if st.button("🚀 Send Emails"):
    if contacts is None:
        st.warning("⚠️ Please upload contacts.csv first.")
    elif not sender or not subject or not body:
        st.warning("⚠️ Please fill sender, subject, and body.")
    else:
        st.info("📨 Sending emails... Please wait.")
        progress = st.progress(0)
        logs = []
        for i, (_, row) in enumerate(contacts.iterrows()):
            personalized = body.replace("{{name}}", row['name'])
            msg = create_message(sender, row['email'], subject, personalized, attachments=attachment_paths)
            status = send_message(service, 'me', msg)
            logs.append({'email': row['email'], 'status': status})
            progress.progress((i + 1) / len(contacts))
        st.success("🎉 All emails sent successfully!")
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.download_button("⬇️ Download Log CSV", data=open("send_log.csv", "rb"), file_name="send_log.csv", mime="text/csv")

# --- Footer ---
st.markdown('<div class="footer">💡 Developed by <b>Nabeel</b> | Built with ❤️ using Streamlit & Gmail API</div>', unsafe_allow_html=True)


