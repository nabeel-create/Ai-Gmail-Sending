# ============================
# 📧 AI Gmail Sender – Multi-User OAuth Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os, base64, pickle
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender – Login & Send Emails")
st.caption("By Nabeel | Each user can login with Google to send emails securely")

# --- Session State for credentials ---
if "creds" not in st.session_state:
    st.session_state.creds = None

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

def send_message(service, message):
    try:
        sent = service.users().messages().send(userId='me', body=message).execute()
        return f"✅ Sent (ID: {sent['id']})"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Google OAuth Login ---
st.subheader("🔑 Login with Google")
if st.session_state.creds is None:
    st.info("Please login to your Gmail account to start sending emails.")
    if st.button("Login with Google"):
        flow = Flow.from_client_secrets_file(
            'client_secret.json', 
            scopes=["https://www.googleapis.com/auth/gmail.send"],
            redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.session_state.flow = flow
        st.markdown(f"[Click here to authenticate]({auth_url})")
        code = st.text_input("Enter the authorization code here")
        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state.creds = creds
            st.success("✅ Login successful! You can now send emails.")

# --- Main Email Sending Interface ---
if st.session_state.creds:
    service = build("gmail", "v1", credentials=st.session_state.creds)
    
    # Upload Contacts
    st.subheader("📁 Upload Contacts")
    uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
    contacts = None
    if uploaded_file:
        contacts = pd.read_csv(uploaded_file)
        st.dataframe(contacts)

    # Upload Attachments
    st.subheader("📎 Upload Attachments (Optional)")
    uploaded_attachments = st.file_uploader("Upload files", type=None, accept_multiple_files=True)
    attachment_paths = []
    if uploaded_attachments:
        for f in uploaded_attachments:
            path = os.path.join(".", f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            attachment_paths.append(path)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # Compose Email
    st.subheader("📝 Compose Email")
    sender_email = st.text_input("Sender Email (Your Gmail)", value="")
    subject = st.text_input("Subject")
    body = st.text_area("Body (use {{name}} for personalization)")

    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contacts.csv first!")
        elif not sender_email or not subject or not body:
            st.warning("Fill all required fields!")
        else:
            st.info("Sending emails...")
            logs = []
            for _, row in contacts.iterrows():
                personalized = body.replace("{{name}}", row['name'])
                msg = create_message(sender_email, row['email'], subject, personalized, attachments=attachment_paths)
                status = send_message(service, msg)
                logs.append({'email': row['email'], 'status': status})
            st.success("✅ All emails processed!")
            st.dataframe(pd.DataFrame(logs))
            pd.DataFrame(logs).to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

    # Logout
    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.creds = None
        st.success("Logged out successfully!")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit & Gmail API")
