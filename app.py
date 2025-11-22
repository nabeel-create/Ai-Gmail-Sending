# ============================
# 📧 AI Gmail Sender – Google OAuth Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import pickle

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender (OAuth Login)")
st.caption("Send personalized Gmail messages securely | Multi-user")

# --- Step 1: Google OAuth Setup ---
st.subheader("🔑 Login with Google")
if "credentials" not in st.session_state:
    st.info("Click below to authenticate with your Gmail account.")
    auth_url = None
    if "flow" not in st.session_state:
        # Configure OAuth flow
        flow = Flow.from_client_secrets_file(
            "client_secret.json",  # Upload your OAuth 2.0 JSON file here
            scopes=["https://www.googleapis.com/auth/gmail.send"],
            redirect_uri="http://localhost:8501"  # For Streamlit Cloud, will open locally
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.session_state["flow"] = flow
    else:
        flow = st.session_state["flow"]
        auth_url, _ = flow.authorization_url(prompt="consent")

    st.markdown(f"[Login with Google]({auth_url})")
    
    # Paste redirect URL after login
    code = st.text_input("Paste the `code` parameter from URL after login")
    if code:
        flow.fetch_token(code=code)
        creds = flow.credentials
        st.session_state["credentials"] = creds_to_dict(creds)
        st.success("✅ Logged in successfully!")

else:
    # Load credentials
    creds_dict = st.session_state["credentials"]
    creds = Credentials(**creds_dict)
    st.success("✅ Already logged in with Google!")

# --- Helper Functions ---
def creds_to_dict(creds):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

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
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, message):
    sent = service.users().messages().send(userId="me", body=message).execute()
    return sent

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

# --- Step 5: Send Emails ---
if st.button("🚀 Send Emails"):
    if "credentials" not in st.session_state:
        st.warning("Please login with Google first!")
        st.stop()
    if contacts is None:
        st.warning("Upload contacts.csv first!")
        st.stop()
    if not subject or not body:
        st.warning("Fill subject and body fields!")
        st.stop()

    # Build Gmail API service
    creds = Credentials(**st.session_state["credentials"])
    service = build("gmail", "v1", credentials=creds)
    st.info("Sending emails...")
    logs = []
    progress_bar = st.progress(0)
    total = len(contacts)

    for idx, row in contacts.iterrows():
        personalized = body.replace("{{name}}", str(row['name']))
        msg = create_message("me", row['email'], subject, personalized, attachments=attachment_paths)
        try:
            sent = send_message(service, msg)
            logs.append({"email": row['email'], "status": f"✅ Sent (ID: {sent['id']})"})
        except Exception as e:
            logs.append({"email": row['email'], "status": f"❌ Error: {e}"})
        progress_bar.progress((idx + 1)/total)

    st.success("✅ All emails processed!")
    st.dataframe(pd.DataFrame(logs))
    pd.DataFrame(logs).to_csv("send_log.csv", index=False)
    st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit & Gmail OAuth API")
