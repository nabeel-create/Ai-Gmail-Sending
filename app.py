# ============================
# 📧 AI Gmail Sender – Streamlit Cloud Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os, base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender by Nabeel", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender")
st.caption("By Nabeel | Send personalized Gmail messages automatically")

# --- Load Secrets ---
client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]
refresh_token = st.secrets["REFRESH_TOKEN"]

# --- Create Gmail Service ---
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
sender = st.text_input("Sender Gmail (authorized)")
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

# --- Send Button ---
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
        st.dataframe(pd.DataFrame(logs))
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit and Gmail API")


