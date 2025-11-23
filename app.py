# ============================
# 📧 AI Gmail Sender – SMTP Version with One-Click Login Redirect
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
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "sender_email" not in st.session_state:
    st.session_state.sender_email = ""
if "sender_password" not in st.session_state:
    st.session_state.sender_password = ""
if "contacts" not in st.session_state:
    st.session_state.contacts = None
if "attachments" not in st.session_state:
    st.session_state.attachments = []

# =========================
# LOGIN PAGE
# =========================
def login_page():
    st.title("🔐 Gmail Login")
    st.subheader("Enter your Gmail credentials")
    
    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail App Password (recommended)", type="password")
    
    if st.button("Login"):
        if not email or not password:
            st.warning("Please fill in both fields!")
        else:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, password)
                server.quit()
                
                # Save credentials in session_state
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = password
                
                # Redirect immediately to email sender page
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Login failed: {e}")

# =========================
# EMAIL SENDER PAGE
# =========================
def email_sender_page():
    st.title("📧 AI Gmail Sender")
    st.caption(f"Logged in as: {st.session_state.sender_email}")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.sender_email = ""
        st.session_state.sender_password = ""
        st.session_state.contacts = None
        st.session_state.attachments = []
        st.experimental_rerun()
    
    # --- Upload Contacts ---
    st.subheader("📁 Upload Contacts")
    uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
    if uploaded_file:
        st.session_state.contacts = pd.read_csv(uploaded_file)
        st.dataframe(st.session_state.contacts)
    
    # --- Upload Attachments ---
    st.subheader("📎 Upload Attachments (optional)")
    uploaded_attachments = st.file_uploader("Upload one or more files", type=None, accept_multiple_files=True)
    if uploaded_attachments:
        st.session_state.attachments = []
        for f in uploaded_attachments:
            path = os.path.join(".", f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            st.session_state.attachments.append(path)
        st.write(f"✅ {len(st.session_state.attachments)} attachment(s) ready")
    
    # --- Compose Email ---
    st.subheader("📝 Compose Email")
    subject = st.text_input("Subject")
    body = st.text_area("Body (use {{name}} for personalization)")
    
    # --- Email Functions ---
    def create_message(sender, to, subject, body_text, attachments=None):
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))
        
        if attachments:
            for path in attachments:
                part = MIMEBase("application", "octet-stream")
                with open(path, "rb") as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                msg.attach(part)
        return msg
    
    def send_email_smtp(sender, password, msg):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            return "✅ Sent"
        except Exception as e:
            return f"❌ Error: {e}"
    
    # --- Send Emails ---
    if st.button("🚀 Send Emails"):
        if st.session_state.contacts is None:
            st.warning("Upload contacts.csv first!")
        elif not subject or not body:
            st.warning("Fill in both subject and body!")
        else:
            st.info("Sending emails...")
            logs = []
            for _, row in st.session_state.contacts.iterrows():
                personalized_body = body.replace("{{name}}", row["name"])
                msg = create_message(
                    st.session_state.sender_email,
                    row["email"],
                    subject,
                    personalized_body,
                    st.session_state.attachments,
                )
                status = send_email_smtp(st.session_state.sender_email, st.session_state.sender_password, msg)
                logs.append({"email": row["email"], "status": status})
            st.success("✅ All emails processed!")
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs)
            df_logs.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# =========================
# PAGE ROUTER
# =========================
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
