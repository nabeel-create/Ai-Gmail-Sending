# ============================
# 📧 AI Gmail Sender – SMTP Version (No OAuth)
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os, json, base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from streamlit_oauth import OAuth2Component

# --- Page Config ---
st.set_page_config(page_title="Professional Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 Professional Gmail Sender")
st.caption("Login with your Gmail to send bulk emails securely")

# --- Google OAuth Setup ---
client_id = st.secrets["google"]["client_id"]
client_secret = st.secrets["google"]["client_secret"]
redirect_uri = st.secrets["google"]["redirect_uri"]

oauth = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

scopes = ["https://www.googleapis.com/auth/gmail.send"]

# --- User Login ---
if "token" not in st.session_state:
    result = oauth.authorize_button("Login with Google", scopes=scopes)
    if result:
        st.session_state.token = result.get('token')
        st.success("Logged in successfully!")
        st.experimental_rerun()

if "token" in st.session_state:
    access_token = st.session_state.token["access_token"]

    # --- Sidebar Navigation ---
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navigate", ["Compose Email", "Templates", "Logs", "Help"])

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

    def send_message(service, message):
        try:
            sent = service.users().messages().send(userId='me', body=message).execute()
            return f"✅ Sent (ID: {sent['id']})"
        except Exception as e:
            return f"❌ Error: {e}"

    # --- Gmail Service ---
    creds = Credentials(
        token=access_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    service = build("gmail", "v1", credentials=creds)

    # --- Pages ---
    if page == "Compose Email":
        st.subheader("📬 Compose Bulk Email")

        # Upload contacts
        uploaded_file = st.file_uploader("Upload contacts CSV (name,email)", type="csv")
        contacts = None
        if uploaded_file:
            contacts = pd.read_csv(uploaded_file)
            st.dataframe(contacts)

        # Upload attachments
        uploaded_attachments = st.file_uploader("Upload attachments (optional)", type=None, accept_multiple_files=True)
        attachment_paths = []
        if uploaded_attachments:
            for f in uploaded_attachments:
                path = os.path.join(".", f.name)
                with open(path, "wb") as out_file:
                    out_file.write(f.getbuffer())
                attachment_paths.append(path)
            st.success(f"{len(attachment_paths)} attachment(s) ready")

        # Email composition
        sender = st.text_input("Sender Gmail", value="me")
        subject = st.text_input("Subject")
        body = st.text_area("Body (use {{name}} for personalization)")

        if st.button("🚀 Send Emails"):
            if contacts is None:
                st.warning("Upload contacts.csv first!")
            elif not subject or not body:
                st.warning("Fill subject and body fields!")
            else:
                st.info("Sending emails...")
                logs = []
                for _, row in contacts.iterrows():
                    personalized = body.replace("{{name}}", row['name'])
                    msg = create_message(sender, row['email'], subject, personalized, attachment_paths)
                    status = send_message(service, msg)
                    logs.append({'email': row['email'], 'status': status})
                st.success("✅ All emails processed!")
                st.dataframe(pd.DataFrame(logs))
                pd.DataFrame(logs).to_csv("send_log.csv", index=False)
                st.info("📁 Log saved as send_log.csv")

    elif page == "Templates":
        st.subheader("📄 Email Templates")
        if not os.path.exists("templates"):
            os.makedirs("templates")
        template_name = st.text_input("Template Name")
        template_subject = st.text_input("Subject")
        template_body = st.text_area("Body")
        if st.button("💾 Save Template"):
            data = {"subject": template_subject, "body": template_body}
            with open(f"templates/{template_name}.json", "w") as f:
                json.dump(data, f)
            st.success(f"Template '{template_name}' saved!")

        st.write("Available Templates:")
        for file in os.listdir("templates"):
            if file.endswith(".json"):
                st.write(file.replace(".json", ""))

    elif page == "Logs":
        st.subheader("📊 Email Logs")
        if os.path.exists("send_log.csv"):
            df_logs = pd.read_csv("send_log.csv")
            st.dataframe(df_logs)
        else:
            st.info("No logs available yet.")

    elif page == "Help":
        st.subheader("💡 Help")
        st.markdown("""
        - Login with your Google account.  
        - Upload a CSV file with contacts.  
        - Compose email with {{name}} for personalization.  
        - Attach files if needed.  
        - Use Templates to save/reuse emails.  
        - Check Logs for sent emails and failures.
        """)

