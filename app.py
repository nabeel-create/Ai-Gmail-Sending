# ============================
# 📧 AI Gmail Sender – SMTP Version (No OAuth)
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import smtplib, ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="AI Gmail Sender (SMTP)", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender – Simple Login (No OAuth)")
st.caption("Send personalized Gmail messages using your App Password")

# -----------------------------------------
# 🔐 Gmail Login
# -----------------------------------------
st.sidebar.header("🔐 Gmail Login")

sender_email = st.sidebar.text_input("Your Gmail Address")
app_password = st.sidebar.text_input("Your Gmail App Password", type="password")

login_ok = False
if st.sidebar.button("Login"):
    if not sender_email or not app_password:
        st.sidebar.error("Please enter Gmail + App Password!")
    else:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, app_password)
            server.quit()
            st.sidebar.success("✅ Login successful!")
            login_ok = True
        except:
            st.sidebar.error("❌ Invalid Gmail or App Password")

# Stop UI until login
if not login_ok:
    st.info("🔐 Please login from the sidebar to continue.")
    st.stop()

# -----------------------------------------
# 📁 Upload Contacts
# -----------------------------------------
st.subheader("📁 Upload Contacts (CSV)")
uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")

contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.dataframe(contacts)

# -----------------------------------------
# 📎 Attachments
# -----------------------------------------
st.subheader("📎 Upload Attachments (Optional)")
uploaded_attachments = st.file_uploader("Upload files", accept_multiple_files=True)

attachment_paths = []
if uploaded_attachments:
    for file in uploaded_attachments:
        path = f"./{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        attachment_paths.append(path)
    st.success(f"Uploaded {len(attachment_paths)} attachment(s).")

# -----------------------------------------
# 📝 Email Composer
# -----------------------------------------
st.subheader("📝 Compose Your Email")

subject = st.text_input("Subject")
body = st.text_area("Email Body (Use {{name}} for personalization)")

# -----------------------------------------
# 📤 Email Sending Function
# -----------------------------------------
def send_email(to, subject, body, attachments):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Attach files
    for file in attachments:
        with open(file, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file)}"
        )
        msg.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to, msg.as_string())

        return "✔ Sent"
    except Exception as e:
        return f"❌ {str(e)}"

# -----------------------------------------
# 🚀 Send Emails Button
# -----------------------------------------
if st.button("🚀 Send Emails"):
    if contacts is None:
        st.warning("Upload contacts.csv first!")
    elif not subject or not body:
        st.warning("Please fill subject and body!")
    else:
        logs = []

        for _, row in contacts.iterrows():
            personalized_body = body.replace("{{name}}", row["name"])
            status = send_email(row["email"], subject, personalized_body, attachment_paths)
            logs.append({"email": row["email"], "status": status})

        log_df = pd.DataFrame(logs)
        st.dataframe(log_df)

        log_df.to_csv("send_log.csv", index=False)
        st.success("🎉 All emails processed!")
        st.info("📁 Log saved as send_log.csv")

st.markdown("----")
st.markdown("💡 **Developed by Nabeel** | Simple Gmail Sender using SMTP + App Password")
