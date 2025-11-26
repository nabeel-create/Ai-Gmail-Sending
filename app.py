# ============================
# 📧 AI Gmail Sender – Red/White Gmail Theme
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
from openai import OpenAI

# ---------------------------
# PAGE SETTINGS
# ---------------------------
st.set_page_config(
    page_title="AI Gmail Sender",
    page_icon="📧",
    layout="wide"
)

# ---------------------------
# CUSTOM GMAIL THEME (RED + WHITE)
# ---------------------------
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 3px solid #EA4335;
}

/* Sidebar menu buttons */
.stButton>button {
    background-color: #EA4335 !important;
    color: white !important;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
}

/* Headers Red */
h1, h2, h3, h4 {
    color: #EA4335;
    font-weight: 700;
}

/* Success banner */
.success-box {
    padding: 15px;
    background: #EA4335;
    color: white;
    border-radius: 8px;
    text-align: center;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------
# SESSION SETUP
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "contacts" not in st.session_state:
    st.session_state.contacts = None


# ---------------------------
# LOGIN PAGE
# ---------------------------
def login_page():

    st.title("🔐 Gmail Login (Red & White Theme)")
    st.subheader("Enter Gmail & App Password")

    st.markdown("""
    👉 **Create Gmail App Password:**  
    🔗 https://myaccount.google.com/apppasswords  
    """)

    email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    password = st.text_input("Gmail App Password", type="password", placeholder="16-digit app password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please fill in all fields.")
            return

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, password)
            server.quit()

            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.password = password

            st.markdown('<div class="success-box">🎉 Login Successful! Welcome to AI Gmail Sender.</div>', unsafe_allow_html=True)

            st.session_state.show_welcome = True
            st.session_state.redirect = True

        except:
            st.error("❌ Login failed! Recheck email or app password.")


# ---------------------------
# EMAIL SENDER PAGE
# ---------------------------
def email_sender_page():
    
    st.sidebar.title("📌 Menu")
    menu = st.sidebar.radio("Navigation", ["Send Emails", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.password = ""
        st.session_state.contacts = None
        st.success("Logged out successfully.")
        return

    # Welcome message after login (only once)
    if st.session_state.get("show_welcome"):
        st.markdown(f'<div class="success-box">👋 Welcome, {st.session_state.email}!</div>', unsafe_allow_html=True)
        st.session_state.show_welcome = False

    st.title("📧 AI Gmail Sender")
    st.caption(f"Logged in as: **{st.session_state.email}**")

    # Upload Contacts
    st.subheader("📁 Upload Contacts CSV")
    file = st.file_uploader("Upload CSV (name,email)", type="csv")
    if file:
        st.session_state.contacts = pd.read_csv(file)
        st.dataframe(st.session_state.contacts)

    # Compose Email Section
    st.subheader("📝 Compose Email")
    subject = st.text_input("Subject")
    body = st.text_area("Body: Use {{name}} to personalize")

    # Generate email with AI
    if st.button("✨ Generate Body with AI"):
        if not st.session_state.get("api_key"):
            st.error("Add your OpenAI API key in sidebar.")
        else:
            try:
                client = OpenAI(api_key=st.session_state.api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Create a polite email."},
                        {"role": "user", "content": "Generate an email body for: " + subject}
                    ]
                )
                ai_text = response.choices[0].message["content"]
                st.success("AI generated email body!")
                st.write(ai_text)
                body = ai_text

            except Exception as e:
                st.error(f"Error generating email: {e}")

    # Send Emails
    if st.button("🚀 Send Emails Now"):
        if st.session_state.contacts is None:
            st.warning("Upload contacts first.")
            return
        if not subject or not body:
            st.warning("Fill subject & body.")
            return

        st.info("Sending emails...")

        logs = []
        for _, row in st.session_state.contacts.iterrows():
            personalized = body.replace("{{name}}", row["name"])

            msg = MIMEMultipart()
            msg["From"] = st.session_state.email
            msg["To"] = row["email"]
            msg["Subject"] = subject
            msg.attach(MIMEText(personalized, "plain"))

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(st.session_state.email, st.session_state.password)
                server.send_message(msg)
                server.quit()
                logs.append({"email": row["email"], "status": "Sent"})
            except:
                logs.append({"email": row["email"], "status": "Failed"})

        df = pd.DataFrame(logs)
        st.dataframe(df)
        df.to_csv("send_log.csv", index=False)
        st.success("📤 All emails processed! Log saved.")


# ---------------------------
# ROUTING
# ---------------------------
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
