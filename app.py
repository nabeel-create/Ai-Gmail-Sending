# ============================
# 📧 AI Gmail Sender – Streamlit Cloud OAuth
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse, parse_qs

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender OAuth", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender – OAuth Version")
st.caption("Send personalized Gmail messages securely | Multi-User Supported")

# --- Step 0: Create client_secret.json from Streamlit Secrets ---
# Streamlit Secrets must have your Google OAuth credentials in TOML:
# [google_oauth]
# client_id = "YOUR_CLIENT_ID"
# client_secret = "YOUR_CLIENT_SECRET"

client_info = {
    "web": {
        "client_id": st.secrets["google_oauth"]["client_id"],
        "client_secret": st.secrets["google_oauth"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["https://ai-gmail-sending-bynabeel.streamlit.app"]
    }
}

with open("client_secret.json", "w") as f:
    json.dump(client_info, f)

# --- Step 1: One-Click Google OAuth Login ---
if "creds" not in st.session_state:
    st.session_state.creds = None

if st.session_state.creds is None:
    st.subheader("🔑 Sign in with Google to send Gmail")
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        redirect_uri='https://ai-gmail-sending-bynabeel.streamlit.app/'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[Click here to authorize Gmail]({auth_url})")

    # Capture the URL after redirect
    redirect_response = st.text_input("Paste the full URL you were redirected to after login:")
    if redirect_response:
        try:
            code = parse_qs(urlparse(redirect_response).query)['code'][0]
            flow.fetch_token(code=code)
            st.session_state.creds = flow.credentials
            st.success("✅ Google account connected successfully!")
        except Exception as e:
            st.error(f"⚠️ OAuth failed: {e}")
else:
    st.success("✅ Already authenticated with Google account")

creds = st.session_state.creds

# --- Step 2: Upload Contacts ---
st.subheader("📁 Upload Contacts")
uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.dataframe(contacts)

# --- Step 3: Upload Attachments ---
st.subheader("📎 Upload Attachments (optional)")
uploaded_attachments = st.file_uploader("Upload one or more files", type=None, accept_multiple_files=True)
attachment_paths = []
if uploaded_attachments:
    for f in uploaded_attachments:
        path = os.path.join(".", f.name)
        with open(path, "wb") as out_file:
            out_file.write(f.getbuffer())
        attachment_paths.append(path)
    st.success(f"{len(attachment_paths)} attachment(s) ready.")

# --- Step 4: Compose Email ---
st.subheader("📝 Compose Email")
subject = st.text_input("Subject")
body = st.text_area("Body (use {{name}} for personalization)")

# --- Email Functions ---
def create_message(sender, to, subject, body_text, attachments=None):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))

    if attachments:
        for path in attachments:
            part = MIMEBase('application', 'octet-stream')
            with open(path, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
            msg.attach(part)
    return msg

def send_email_oauth(creds, to_email, subject, body, attachments=None):
    try:
        sender_email = creds.token_info['email']
        msg = create_message(sender_email, to_email, subject, body, attachments)
        access_token = creds.token
        auth_string = f"user={sender_email}\1auth=Bearer {access_token}\1\1"
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string.encode()).decode())
            server.sendmail(sender_email, to_email, msg.as_string())
        return "✅ Sent"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Step 5: Send Emails ---
if st.button("🚀 Send Emails"):
    if creds is None:
        st.warning("Authenticate with Google first!")
    elif contacts is None:
        st.warning("Upload contacts.csv first!")
    elif not subject or not body:
        st.warning("Fill subject and body fields!")
    else:
        st.info("Sending emails...")
        logs = []
        progress_bar = st.progress(0)
        total = len(contacts)
        for idx, row in contacts.iterrows():
            personalized = body.replace("{{name}}", str(row['name']))
            status = send_email_oauth(creds, row['email'], subject, personalized, attachments=attachment_paths)
            logs.append({'email': row['email'], 'status': status})
            progress_bar.progress((idx + 1)/total)
        st.success("✅ All emails processed!")
        st.dataframe(pd.DataFrame(logs))
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit & Gmail OAuth")
