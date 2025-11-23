# ============================
# 📧 AI Gmail Sender – SMTP Version
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender by Nabeel", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender (SMTP Version)")
st.caption("By Nabeel | Send Gmail using your own account securely")

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
sender_email = st.text_input("Your Gmail Address")
sender_password = st.text_input("Your Gmail Password (App Password recommended)", type="password")
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

def send_email_smtp(sender, password, to, msg):
    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return "✅ Sent"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Send Button ---
if st.button("🚀 Send Emails"):
    if contacts is None:
        st.warning("Upload contacts.csv first!")
    elif not sender_email or not sender_password or not subject or not body:
        st.warning("Fill all fields!")
    else:
        st.info("Sending emails...")
        logs = []
        for _, row in contacts.iterrows():
            personalized = body.replace("{{name}}", row['name'])
            msg = create_message(sender_email, row['email'], subject, personalized, attachment_paths)
            status = send_email_smtp(sender_email, sender_password, row['email'], msg)
            logs.append({'email': row['email'], 'status': status})
        st.success("✅ All emails processed!")
        st.dataframe(pd.DataFrame(logs))
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit and SMTP")
