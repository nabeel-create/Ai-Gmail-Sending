import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="SMTP Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 Gmail Sender via SMTP (App Password)")

# --- User Inputs ---
st.subheader("Login with your Gmail")
sender_email = st.text_input("Gmail address")
app_password = st.text_input("App Password", type="password")

# --- Upload Contacts ---
st.subheader("Upload Contacts CSV")
uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.dataframe(contacts)

# --- Upload Attachments ---
st.subheader("Upload Attachments (optional)")
uploaded_attachments = st.file_uploader("Upload files", type=None, accept_multiple_files=True)
attachment_paths = []
if uploaded_attachments:
    for f in uploaded_attachments:
        path = os.path.join(".", f.name)
        with open(path, "wb") as out_file:
            out_file.write(f.getbuffer())
        attachment_paths.append(path)

# --- Compose Email ---
st.subheader("Compose Email")
subject = st.text_input("Subject")
body = st.text_area("Body (use {{name}} for personalization)")

# --- Functions ---
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

def send_email(sender, password, recipient, msg):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        return "✅ Sent"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Send Emails ---
if st.button("🚀 Send Emails"):
    if not sender_email or not app_password:
        st.warning("Enter Gmail and App Password!")
    elif contacts is None:
        st.warning("Upload contacts CSV first!")
    elif not subject or not body:
        st.warning("Fill subject and body fields!")
    else:
        st.info("Sending emails...")
        logs = []
        for _, row in contacts.iterrows():
            personalized = body.replace("{{name}}", row['name'])
            msg = create_message(sender_email, row['email'], subject, personalized, attachment_paths)
            status = send_email(sender_email, app_password, row['email'], msg)
            logs.append({"email": row['email'], "status": status})
        st.success("✅ All emails processed!")
        st.dataframe(pd.DataFrame(logs))
        pd.DataFrame(logs).to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

