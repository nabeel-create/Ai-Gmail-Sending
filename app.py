# ============================
# 📧 AI Gmail Sender – Pro Beautiful Edition
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

# --- Custom CSS for Stunning UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    .main {
        background: linear-gradient(135deg, #f6f9ff 0%, #e9f1ff 100%);
        font-family: 'Poppins', sans-serif;
        color: #222;
        padding: 10px 40px;
    }

    /* HEADER */
    .app-header {
        background: linear-gradient(90deg, #0061ff, #60efff);
        padding: 30px 10px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(0, 97, 255, 0.3);
        margin-bottom: 30px;
        animation: slideDown 1s ease-out;
    }
    .app-header h1 {
        font-size: 45px;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 6px;
        text-shadow: 0 0 10px rgba(255,255,255,0.7);
    }
    .app-header p {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.95);
    }
    @keyframes slideDown {
        from {transform: translateY(-25px); opacity: 0;}
        to {transform: translateY(0); opacity: 1;}
    }

    /* CARDS */
    .card {
        background: white;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    }

    /* FOOTER */
    .footer {
        text-align: center;
        margin-top: 60px;
        padding: 25px;
        font-size: 15px;
        color: #555;
        border-top: 1px solid #ddd;
        background: linear-gradient(90deg, #ffffff 0%, #f8faff 100%);
        border-radius: 16px;
        box-shadow: 0 -2px 20px rgba(0,0,0,0.05);
        animation: fadeIn 1.5s ease-in;
    }
    .footer b {
        background: -webkit-linear-gradient(45deg, #0061ff, #60efff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        animation: glow 2s infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 5px #0061ff, 0 0 10px #60efff; }
        to { text-shadow: 0 0 15px #60efff, 0 0 25px #00f2ff; }
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #0072ff, #00c6ff);
        color: white;
        border: none;
        padding: 0.6em 2em;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,114,255,0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #005be7, #00a6ff);
        box-shadow: 0 6px 18px rgba(0,114,255,0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="app-header">
    <h1>📧 AI Gmail Sender</h1>
    <p>Welcome to your Smart Email Automation System — powered by AI & built by <b>Nabeel</b> 💫</p>
</div>
""", unsafe_allow_html=True)

# --- Loading Animation ---
with st.spinner("🚀 Initializing AI Gmail Sender..."):
    time.sleep(1.8)

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
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📁 Upload Contacts")
uploaded_file = st.file_uploader("Upload your contacts CSV file (columns: name,email)", type="csv")
contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.dataframe(contacts, use_container_width=True)
    st.success(f"✅ {len(contacts)} contacts loaded")
st.markdown('</div>', unsafe_allow_html=True)

# --- Upload Attachments ---
st.markdown('<div class="card">', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)

# --- Compose Email ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📝 Compose Email")
col1, col2 = st.columns(2)
with col1:
    sender = st.text_input("Sender Gmail (authorized):")
    subject = st.text_input("Email Subject:")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("💡 Use **{{name}}** in your email body for personalization.")
body = st.text_area("✉️ Email Body", height=200, placeholder="Hello {{name}},\n\nThis is an automated email from Nabeel's AI Gmail Sender...")
st.markdown('</div>', unsafe_allow_html=True)

# --- Email Sending Functions ---
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

# --- Send Emails ---
st.markdown('<div class="card">', unsafe_allow_html=True)
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
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df, use_container_width=True)
        log_df.to_csv("send_log.csv", index=False)
        st.download_button("⬇️ Download Log CSV", data=open("send_log.csv", "rb"), file_name="send_log.csv", mime="text/csv")
st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    <p>💌 Thank you for using <b>AI Gmail Sender</b><br>
    Developed with ❤️ by <b>Nabeel</b> | Built using Streamlit × Gmail API | © 2025</p>
</div>
""", unsafe_allow_html=True)
