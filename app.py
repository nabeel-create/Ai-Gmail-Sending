# ============================
# 📧 AI Gmail Sender – SMTP Version with Login & Multi-Page
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
    st.title("🔐 Login to Gmail")
    st.subheader("Enter your Gmail credentials to proceed")
    
    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail Password (App Password recommended)", type="password")
    
    if st.button("Login"):
        if not email or not password:
            st.warning("Please fill all fields!")
        else:
            try:
                # Test SMTP login
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                server.quit()
                
                # Save credentials in session
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = password
                st.success("✅ Login successful!")
            except Exception as e:
                st.error(f"❌ Login failed: {e}")

# =========================
# CONTACTS & ATTACHMENTS PAGE
# =========================
def contacts_attachments_page():
    st.sidebar.title("📋 Dashboard")
    st.sidebar.write(f"Logged in as: {st.session_state.sender_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.sender_email = ""
        st.session_state.sender_password = ""
        st.session_state.contacts = None
        st.session_state.attachments = []
        st.experimental_rerun()
    
    st.title("📁 Contacts & Attachments")
    
    # Upload Contacts
    st.subheader("Upload Contacts")
    uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
    if uploaded_file:
        st.session_state.contacts = pd.read_csv(uploaded_file)
        st.dataframe(st.session_state.contacts)
    
    # Upload Attachments
    st.subheader("Upload Attachments (optional)")
    uploaded_attachments = st.file_uploader("Upload one or more files", type=None, accept_multiple_files=True)
    if uploaded_attachments:
        st.session_state.attachments = []
        for f in uploaded_attachments:
            path = os.path.join(".", f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            st.session_state.attachments.append(path)
        st.write(f"✅ {len(st.session_state.attachments)} attachment(s) ready")
    
    if st.session_state.contacts is not None:
        if st.button("Go to Email Composer"):
            st.session_state.page = "compose"

# =========================
# EMAIL COMPOSER PAGE
# =========================
def email_composer_page():
    st.sidebar.title("📋 Dashboard")
    st.sidebar.write(f"Logged in as: {st.session_state.sender_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.sender_email = ""
        st.session_state.sender_password = ""
        st.session_state.contacts = None
        st.session_state.attachments = []
        st.session_state.page = "login"
        st.experimental_rerun()
    if st.sidebar.button("Back to Contacts"):
        st.session_state.page = "contacts"
        st.experimental_rerun()
    
    st.title("📝 Compose Email")
    
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
    
    def send_email_smtp(sender, password, msg):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            return "✅ Sent"
        except Exception as e:
            return f"❌ Error: {e}"
    
    # Send Button
    if st.button("🚀 Send Emails"):
        if st.session_state.contacts is None:
            st.warning("Upload contacts first!")
        elif not subject or not body:
            st.warning("Fill all fields!")
        else:
            st.info("Sending emails...")
            logs = []
            for _, row in st.session_state.contacts.iterrows():
                personalized = body.replace("{{name}}", row['name'])
                msg = create_message(st.session_state.sender_email, row['email'], subject, personalized, st.session_state.attachments)
                status = send_email_smtp(st.session_state.sender_email, st.session_state.sender_password, msg)
                logs.append({'email': row['email'], 'status': status})
            st.success("✅ All emails processed!")
            st.dataframe(pd.DataFrame(logs))
            pd.DataFrame(logs).to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# =========================
# PAGE ROUTER
# =========================
if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "contacts":
    contacts_attachments_page()
elif st.session_state.page == "compose":
    email_composer_page()
