# ============================
# 📧 AI Gmail Sender – Google OAuth Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os, base64, json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="AI Gmail Sender Login", layout="wide")
st.title("📧 AI Gmail Sender with Google Login")

# -----------------------------
# 🔐 Load Client Secrets JSON
# -----------------------------
client_secret_json = {
    "web": {
        "client_id": st.secrets["CLIENT_ID"],
        "project_id": "gmail-sender",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_secret": st.secrets["CLIENT_SECRET"],
        "redirect_uris": ["https://YOUR-STREAMLIT-APP-URL"],
        "javascript_origins": ["https://YOUR-STREAMLIT-APP-URL"]
    }
}

# ---------------------------------
# 🔐 Google OAuth Settings
# ---------------------------------
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

if "creds" not in st.session_state:
    st.session_state.creds = None

# ---------------------------------
# 📌 Step 1: Google Login Button
# ---------------------------------
if st.session_state.creds is None:
    auth_url = None

    if st.button("🔐 Login with Google"):
        flow = Flow.from_client_config(
            client_secret_json,
            scopes=SCOPES,
            redirect_uri="https://YOUR-STREAMLIT-APP-URL"
        )

        auth_url, _ = flow.authorization_url(prompt="consent")

        st.write("### Click below to login:")
        st.markdown(f"[👉 Login to Google]({auth_url})")

    # Handle OAuth Response
    query_params = st.experimental_get_query_params()

    if "code" in query_params:
        code = query_params["code"][0]
        flow = Flow.from_client_config(
            client_secret_json,
            scopes=SCOPES,
            redirect_uri="https://YOUR-STREAMLIT-APP-URL"
        )
        flow.fetch_token(code=code)
        st.session_state.creds = flow.credentials
        st.success("✅ Google Login Successful! You can now send emails.")

# ---------------------------------
# 🎯 If Logged In → Gmail Sender UI
# ---------------------------------
if st.session_state.creds:

    service = build("gmail", "v1", credentials=st.session_state.creds)
    st.success("🔗 Gmail API Connected")

    st.subheader("📁 Upload Contacts")
    uploaded_file = st.file_uploader("Upload CSV (name,email)", type="csv")
    if uploaded_file:
        contacts = pd.read_csv(uploaded_file)
        st.dataframe(contacts)

    st.subheader("📎 Upload Attachments (Optional)")
    uploaded_attachments = st.file_uploader(
        "Upload one or more files",
        accept_multiple_files=True
    )

    paths = []
    if uploaded_attachments:
        for f in uploaded_attachments:
            p = f"./{f.name}"
            with open(p, "wb") as out:
                out.write(f.getbuffer())
            paths.append(p)

    st.subheader("📝 Compose Email")
    subject = st.text_input("Subject")
    body = st.text_area("Email Body (Use {{name}})")

    # ---------------------------------
    # 📤 Send Email Function
    # ---------------------------------
    def create_message(to, subject, body, attachments):
        msg = MIMEMultipart()
        msg["to"] = to
        msg["subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach files
        for file in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(open(file, "rb").read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file)}"
            )
            msg.attach(part)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return {"raw": raw}

    def send_email(to, subject, body):
        msg = create_message(to, subject, body, paths)
        try:
            result = service.users().messages().send(userId="me", body=msg).execute()
            return "Sent ✔"
        except Exception as e:
            return str(e)

    # ---------------------------------
    # 🚀 Send Button
    # ---------------------------------
    if st.button("🚀 Send Emails"):
        if not uploaded_file:
            st.warning("Upload contacts.csv")
        else:
            logs = []

            for _, row in contacts.iterrows():
                personalized_body = body.replace("{{name}}", row["name"])
                status = send_email(row["email"], subject, personalized_body)
                logs.append({"email": row["email"], "status": status})

            df = pd.DataFrame(logs)
            st.dataframe(df)
            df.to_csv("send_log.csv", index=False)
            st.success("✔ All emails processed")

