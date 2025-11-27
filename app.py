# ================================================
# 📧 AI Gmail Sender – Auto Subject & Body from Description
# Model: meta-llama/llama-3.3-70b-instruct:free
# ================================================

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from openai import OpenAI

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")

# ------------------------
# SESSION STATE INIT
# ------------------------
for key in [
    "logged_in", "sender_email", "sender_password", "show_welcome",
    "generated_body", "generated_subject"
]:
    if key not in st.session_state:
        st.session_state[key] = "" if "email" in key or "password" in key else False

# ------------------------
# CUSTOM CSS
# ------------------------
st.markdown("""
<style>
body {background-color: #f5f5f5;}
.login-box {background: white; width: 400px; padding: 40px; border-radius: 12px; margin: auto; margin-top: 100px; box-shadow: 0px 4px 15px rgba(0,0,0,0.15); border-top: 5px solid #d93025;}
.login-btn {background-color: #d93025 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 600 !important;}
section[data-testid="stSidebar"] {background-color: white; border-right: 2px solid #e3e3e3;}
.sidebar-title {font-size: 22px; font-weight: bold; color: #d93025;}
.welcome-popup {position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%); padding: 20px 30px; background: #d93025; color: white; font-size: 20px; text-align: center; border-radius: 12px; animation: fadeout 3s forwards; z-index: 9999;}
@keyframes fadeout {0% {opacity:1;} 70% {opacity:1;} 100% {opacity:0;}}
</style>
""", unsafe_allow_html=True)

# ------------------------
# HELP MENU (Updated with 2FA instructions)
# ------------------------
def help_menu():
    with st.expander("⋮ How to Enable 2FA & Create Gmail App Password"):
        st.markdown("""
### 🔐 Step 1 — Turn ON 2-Step Verification (Required)
1. Open Google Security Settings: [Enable 2FA](https://myaccount.google.com/security)  
2. Scroll to **"Signing in to Google"**
3. Click **2-Step Verification**
4. Turn it **ON**

---

### 🔑 Step 2 — Create Gmail App Password
(Needed for login in this app — Gmail does not allow normal password)

1. Go to App Passwords: [Create App Password](https://myaccount.google.com/apppasswords)  
2. Sign in again
3. Select **Mail**
4. Select **Other (Custom)**
5. Type: **AI Gmail Sender**
6. Click **Generate**
7. Copy the **16-digit password** and paste it here

---

### 📌 Important Notes
- Normal Gmail password **will NOT work**  
- App Password works even if less-secure apps are blocked  
- You can delete & regenerate anytime  
""")

# ------------------------
# OPENROUTER AI FUNCTION
# ------------------------
def generate_email_via_openrouter(prompt):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["openrouter"]["api_key"]
        )
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a professional email writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating email: {e}"

# ------------------------
# LOGIN PAGE (App Password Only)
# ------------------------
def login_page():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png", width=80)
    st.markdown("### Sign in to continue")

    email = st.text_input("Gmail Address", value=st.session_state.sender_email)

    # App Password Only
    app_password = st.text_input(
        "Gmail App Password (16-digit)",
        type="password",
        value=st.session_state.sender_password
    )

    # Links for 2FA & App Password
    st.markdown(
        """
        <a href='https://myaccount.google.com/security' target='_blank'>🔗 Enable 2-Step Verification</a><br>
        <a href='https://myaccount.google.com/apppasswords' target='_blank'>🔗 Create Gmail App Password</a>
        """,
        unsafe_allow_html=True
    )

    help_menu()

    if st.button("Login"):
        if not email or not app_password:
            st.warning("Enter Email & App Password")
        else:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, app_password)
                server.quit()

                # Save session
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = app_password
                st.session_state.show_welcome = True

                st.rerun()  # instant redirect

            except Exception as e:
                st.error(f"Login failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# EMAIL SENDER PAGE
# ------------------------
def email_sender_page():
    if st.session_state.show_welcome:
        st.markdown("<div class='welcome-popup'>🎉 Welcome to AI Gmail Sending System!</div>", unsafe_allow_html=True)
        st.session_state.show_welcome = False

    st.sidebar.markdown("<p class='sidebar-title'>📧 AI Gmail Sender</p>", unsafe_allow_html=True)
    st.sidebar.write(f"Signed in as: *{st.session_state.sender_email}*")

    # ------------------------ LOGOUT ------------------------
    if st.sidebar.button("Logout"):
        st.session_state.clear()  # wipe all
        st.rerun()                # redirect

    st.title("📤 Send Email")

    # ------------------------ UPLOAD CONTACTS ------------------------
    contacts_file = st.file_uploader("📁 Upload Contacts CSV (name,email)", type="csv")
    contacts = pd.read_csv(contacts_file) if contacts_file else None
    if contacts is not None:
        st.dataframe(contacts)

    # ------------------------ UPLOAD ATTACHMENTS ------------------------
    files = st.file_uploader("📎 Upload attachments", accept_multiple_files=True)
    attachment_paths = []
    if files:
        for f in files:
            with open(f.name, "wb") as out:
                out.write(f.getbuffer())
            attachment_paths.append(f.name)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # ------------------------ EMAIL DESCRIPTION ------------------------
    description = st.text_area("📌 Enter Email Description (what the email should say)")

    if st.button("🤖 Auto Generate Subject & Email"):
        if not description:
            st.warning("Please enter a description first!")
        else:
            prompt = f"""
            Based on the following description, write a professional email.

            Description: {description}

            Return output as:
            Subject: <subject line>
            Body: <email body>
            """
            ai_response = generate_email_via_openrouter(prompt)

            if "Subject:" in ai_response and "Body:" in ai_response:
                st.session_state.generated_subject = ai_response.split("Subject:")[1].split("Body:")[0].strip()
                st.session_state.generated_body = ai_response.split("Body:")[1].strip()
            else:
                st.session_state.generated_subject = "Generated Subject"
                st.session_state.generated_body = ai_response

    # ------------------------ DISPLAY SUBJECT & BODY ------------------------
    subject = st.text_input("Subject", value=st.session_state.generated_subject)
    body = st.text_area("Email Body", value=st.session_state.generated_body, height=200)

    # ------------------------ SEND EMAIL FUNCTIONS ------------------------
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
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
            msg.attach(part)
        return msg

    def send_email(to, msg):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(st.session_state.sender_email, st.session_state.sender_password)
            server.send_message(msg)
            server.quit()
            return "✅ Sent"
        except Exception as e:
            return f"❌ {e}"

    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contact list first!")
        elif not subject or not body:
            st.warning("Fill all fields or generate AI email!")
        else:
            logs = []
            for _, row in contacts.iterrows():
                text_to_send = body.replace("{{name}}", str(row.get("name", "")))
                msg = create_message(st.session_state.sender_email, row["email"], subject, text_to_send, attachment_paths)
                status = send_email(row["email"], msg)
                logs.append({"email": row["email"], "status": status})
            df = pd.DataFrame(logs)
            st.success("All emails processed!")
            st.dataframe(df)
            df.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# ------------------------
# MAIN ROUTER
# ------------------------
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
