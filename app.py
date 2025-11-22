# ============================
# 📧 AI Gmail Sender – Multi-User Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import smtplib

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender")
st.caption("Send personalized Gmail messages easily | Multi-User Supported")

# --- Step 1: User Gmail Login ---
st.subheader("🔑 Gmail Login")
st.info("You need to enter your Gmail and App Password (for accounts with 2FA) or normal password if 2FA is off.")
user_email = st.text_input("Your Gmail")
user_password = st.text_input("App Password / Gmail Password", type="password")

if not user_email or not user_password:
    st.warning("Enter your Gmail and password to proceed.")
    st.stop()

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

def send_email_smtp(sender_email, password, to_email, subject, body, attachments=None):
    try:
        msg = create_message(sender_email, to_email, subject, body, attachments)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return "✅ Sent"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Step 5: Send Emails ---
if st.button("🚀 Send Emails"):
    if contacts is None:
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
            status = send_email_smtp(user_email, user_password, row['email'], subject, personalized, attachments=attachment_paths)
            logs.append({'email': row['email'], 'status': status})
            progress_bar.progress((idx + 1)/total)
        st.success("✅ All emails processed!")
        st.dataframe(pd.DataFrame(logs))
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit & SMTP")
