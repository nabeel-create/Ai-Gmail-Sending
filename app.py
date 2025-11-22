# ============================
# 📧 AI Gmail Sender – Gmail Password Only
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender")
st.caption("Send personalized Gmail messages easily | Gmail Password Only")

# --- Step 1: Gmail Login (Gmail Password Only) ---
st.subheader("🔑 Gmail Login")
st.info("""
Enter your **Gmail address** and **Gmail password**.  

⚠️ Note: Your account must have **2FA disabled** and allow **less secure apps**:
https://myaccount.google.com/lesssecureapps
""")

user_email = st.text_input("Your Gmail")
user_password = st.text_input("Gmail Password", type="password")

login_status = False

if st.button("🔐 Login with Gmail Password"):
    try:
        # Try SMTP login using Gmail password
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user_email, user_password)

        st.success("✅ Login successful! You can now send emails.")
        login_status = True

    except smtplib.SMTPAuthenticationError:
        st.error("""
❌ Login failed! Possible reasons:
- Wrong Gmail password
- 2FA is enabled (must disable to use Gmail password)
- Less secure apps access is disabled

Please correct your password or update your Google account settings.
""")
    except Exception as e:
        st.error(f"⚠️ Login Error: {e}")

# Stop the app until login is successful
if not login_status:
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

    st.success(f"{len(attachment_paths)} attachment(s) uploaded.")

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

        return "✅ Sent Successfully"

    except Exception as e:
        return f"❌ Error: {e}"

# --- Step 5: Send Emails ---
if st.button("🚀 Send Emails"):
    if contacts is None:
        st.warning("Upload contacts.csv first!")
    elif not subject or not body:
        st.warning("Enter both subject and body!")
    else:
        st.info("📨 Sending emails...")

        logs = []
        progress = st.progress(0)
        total = len(contacts)

        for idx, row in contacts.iterrows():
            personalized_body = body.replace("{{name}}", str(row['name']))
            status = send_email_smtp(
                user_email,
                user_password,
                row['email'],
                subject,
                personalized_body,
                attachments=attachment_paths
            )

            logs.append({"email": row['email'], "status": status})
            progress.progress((idx + 1) / total)

        st.success("🎉 All emails processed!")
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df)

        log_df.to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit & SMTP")
