# =====================================================
# 📧 AI Gmail Sender – Gmail Theme (Red & White)
# Author: Nabeel
# =====================================================

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="AI Gmail Sender",
    page_icon="📧",
    layout="wide"
)

# -----------------------------------------------------
# SESSION STATE INIT
# -----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "sender_email" not in st.session_state:
    st.session_state.sender_email = ""
if "sender_password" not in st.session_state:
    st.session_state.sender_password = ""
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False

# -----------------------------------------------------
# CUSTOM CSS (Gmail Theme)
# -----------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f5f5;
}

/* LOGIN PAGE BOX */
.login-box {
    background: white;
    width: 400px;
    padding: 40px;
    border-radius: 12px;
    margin: auto;
    margin-top: 100px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    border-top: 5px solid #d93025; /* Gmail red */
}

/* RED LOGIN BUTTON */
.login-btn {
    background-color: #d93025 !important;
    color: white !important;
    width: 100%;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* SIDEBAR Gmail Colors */
section[data-testid="stSidebar"] {
    background-color: white;
    border-right: 2px solid #e3e3e3;
}

.sidebar-title {
    font-size: 22px;
    font-weight: bold;
    color: #d93025;
}

/* WELCOME POPUP */
.welcome-popup {
    padding: 15px;
    background: #d93025;
    color: white;
    font-size: 18px;
    text-align: center;
    border-radius: 8px;
    animation: fadeout 3s forwards;
    margin-bottom: 10px;
}

@keyframes fadeout {
  0% {opacity: 1;}
  60% {opacity: 1;}
  100% {opacity: 0;}
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# LOGIN PAGE
# -----------------------------------------------------
def login_page():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png",
        width=80
    )
    st.markdown("### Sign in to continue")

    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail App Password", type="password")

    # Direct App Password link
    st.markdown(
        "<a href='https://myaccount.google.com/apppasswords' target='_blank'>"
        "<b>🔗 Create Gmail App Password</b></a>",
        unsafe_allow_html=True
    )

    # Use a CSS class on the login button (visual only)
    if st.button("Login", key="login_button"):
        if not email or not password:
            st.warning("Please enter both Email and App Password")
        else:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, password)
                server.quit()

                # Save session
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = password
                st.session_state.show_welcome = True

                st.success("Login successful! Redirecting...")
                st.rerun()   # ✅ correct API

            except Exception as e:
                st.error(f"Login failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------
# EMAIL SENDER PAGE
# -----------------------------------------------------
def email_sender_page():
    # Top welcome popup (auto fade using CSS only)
    if st.session_state.show_welcome:
        st.markdown(
            "<div class='welcome-popup'>🎉 Welcome to AI Gmail Sending System!</div>",
            unsafe_allow_html=True
        )
        # Only show once; CSS handles fading out
        st.session_state.show_welcome = False

    # Sidebar
    st.sidebar.markdown(
        "<p class='sidebar-title'>📧 AI Gmail Sender</p>",
        unsafe_allow_html=True
    )
    st.sidebar.write(f"Signed in as: **{st.session_state.sender_email}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.sender_email = ""
        st.session_state.sender_password = ""
        st.rerun()   # ✅ correct API

    st.title("📤 Send Email")

    # --- Upload Contacts ---
    st.subheader("📁 Upload Contacts CSV")
    contacts_file = st.file_uploader(
        "Upload contact list (columns: name,email)",
        type="csv"
    )

    contacts = None
    if contacts_file:
        contacts = pd.read_csv(contacts_file)
        st.dataframe(contacts)

    # --- Attachments ---
    st.subheader("📎 Add Attachments (optional)")
    files = st.file_uploader("Upload files", accept_multiple_files=True)
    attachment_paths = []

    if files:
        for file in files:
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            attachment_paths.append(file.name)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # --- Compose Email ---
    st.subheader("📝 Compose Email")
    subject = st.text_input("Subject")
    body = st.text_area("Body (use {{name}} for personalization)")

    def create_message(sender, to, subject, text, attachments):
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))

        for path in attachments:
            part = MIMEBase("application", "octet-stream")
            with open(path, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(path)}"
            )
            msg.attach(part)

        return msg

    def send_email(to, msg):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(
                st.session_state.sender_email,
                st.session_state.sender_password
            )
            server.send_message(msg)
            server.quit()
            return "✅ Sent"
        except Exception as e:
            return f"❌ {e}"

    # --- Send Button ---
    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contact list first!")
        elif not subject or not body:
            st.warning("Fill all fields (subject & body)!")
        else:
            logs = []
            with st.spinner("Sending emails..."):
                for _, row in contacts.iterrows():
                    text = body.replace("{{name}}", str(row["name"]))
                    msg = create_message(
                        st.session_state.sender_email,
                        row["email"],
                        subject,
                        text,
                        attachment_paths,
                    )
                    status = send_email(row["email"], msg)
                    logs.append({"email": row["email"], "status": status})

            df = pd.DataFrame(logs)
            st.success("All emails processed!")
            st.dataframe(df)
            df.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")


# -----------------------------------------------------
# ROUTER
# -----------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
