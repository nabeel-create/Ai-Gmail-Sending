# ============================
# 📧 AI Gmail Sender – Beautiful Login + Full App
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

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="centered")

# --------------------------
# SESSION STATE FOR LOGIN
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# --------------------------
# BEAUTIFUL LOGIN PAGE
# --------------------------
def login_page():

    st.markdown("""
        <style>
            .login-card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                max-width: 420px;
                margin: auto;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                text-align: center;
            }
            .login-title {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 10px;
                color: #333;
            }
            .sub {
                color: #666;
                font-size: 14px;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='login-title'>🔐 Gmail Login</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Login with your Gmail to continue</div>", unsafe_allow_html=True)

    gmail = st.text_input("Enter Gmail Address")
    password = st.text_input("App Password / Gmail Password", type="password")

    login_button = st.button("Login")

    if login_button:
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail, password)

            st.success("Login successful! 🎉")
            st.session_state.logged_in = True
            st.session_state.gmail = gmail
            st.session_state.password = password
            st.experimental_rerun()

        except smtplib.SMTPAuthenticationError:
            st.error("❌ Wrong password or invalid App Password. Try again.")
        except Exception as e:
            st.error(f"⚠️ Login Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# MAIN EMAIL SENDER APP
# --------------------------
def app_page():

    st.title("📧 AI Gmail Sender")
    st.caption("Welcome! You are logged in as **" + st.session_state.gmail + "**")

    st.markdown("---")

    # --- Upload Contacts ---
    st.subheader("📁 Upload Contacts")
    uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
    contacts = None
    if uploaded_file:
        contacts = pd.read_csv(uploaded_file)
        st.dataframe(contacts)

    # --- Upload Attachments ---
    st.subheader("📎 Upload Attachments (optional)")
    uploaded_attachments = st.file_uploader("Upload files", type=None, accept_multiple_files=True)

    attachment_paths = []
    if uploaded_attachments:
        for f in uploaded_attachments:
            path = os.path.join(".", f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            attachment_paths.append(path)
        st.success(f"Uploaded {len(attachment_paths)} attachment(s).")

    # --- Compose Email ---
    st.subheader("📝 Compose Email")
    subject = st.text_input("Subject")
    body = st.text_area("Body (Use {{name}} for personalization)")

    # Email functions
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

    # --- Send button ---
    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contacts.csv first!")
        elif not subject or not body:
            st.warning("Enter subject & body!")
        else:
            st.info("Sending emails, please wait...")
            logs = []
            progress = st.progress(0)
            total = len(contacts)

            for i, row in contacts.iterrows():
                personalized = body.replace("{{name}}", str(row['name']))
                status = send_email_smtp(
                    st.session_state.gmail,
                    st.session_state.password,
                    row['email'],
                    subject,
                    personalized,
                    attachments=attachment_paths
                )
                logs.append({"email": row['email'], "status": status})
                progress.progress((i + 1) / total)

            st.success("🎉 Emails sent!")
            st.dataframe(pd.DataFrame(logs))

            pd.DataFrame(logs).to_csv("send_log.csv", index=False)
            st.info("Log saved as send_log.csv")

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()


# --------------------------
# APP FLOW CONTROLLER
# --------------------------
if not st.session_state.logged_in:
    login_page()
else:
    app_page()
