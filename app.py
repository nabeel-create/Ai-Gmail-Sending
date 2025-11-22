# ============================
# 📧 AI Gmail Sender – Multi-User Version (with Instructions)
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")
st.title("📧 AI Gmail Sender")
st.caption("Send personalized Gmail messages easily | Supports Attachments | Multi-User Login")

# -------------------------------------------------------------
# 🔰 SECTION 0 – USER INSTRUCTIONS
# -------------------------------------------------------------
with st.expander("📘 Instructions (Read Before Using)", expanded=True):
    st.markdown("""
### ✅ **How to Use This App**
1. **Login with your Gmail + App Password**  
   Normal Gmail password **will NOT work** if 2FA is enabled.

2. **Create App Password (Required for most users)**  
   Google blocks third-party apps unless you create an app password.

### 🔐 **How to Generate Your App Password**
➡️ Click the button below to open App Password page:  

👉 **https://myaccount.google.com/apppasswords**

### Steps:
1. Login to your Google account  
2. Enable 2-Step Verification (if not enabled)  
3. Open App Passwords  
4. Choose: **Mail**  
5. Choose: **Windows Computer**  
6. Google gives you a 16-character password  
7. Copy & paste that into this app

⚠️ Never share your app password with anyone.
""")

# -------------------------------------------------------------
# 🔑 SECTION 1 – User Gmail Login
# -------------------------------------------------------------
st.subheader("🔑 Login With Gmail")

user_email = st.text_input("✉️ Enter Your Gmail Address")
user_password = st.text_input("🔐 Enter Your Gmail App Password", type="password")

if not user_email or not user_password:
    st.info("Enter your Gmail + App Password to continue.")
    st.stop()

# -------------------------------------------------------------
# 📁 SECTION 2 – Upload Contacts
# -------------------------------------------------------------
st.subheader("📁 Upload Contacts CSV")

uploaded_file = st.file_uploader("Upload contacts.csv (columns: name,email)", type="csv")
contacts = None
if uploaded_file:
    contacts = pd.read_csv(uploaded_file)
    st.success("Contacts loaded successfully!")
    st.dataframe(contacts)

# -------------------------------------------------------------
# 📎 SECTION 3 – Upload Attachments
# -------------------------------------------------------------
st.subheader("📎 Attach Files (optional)")

uploaded_attachments = st.file_uploader(
    "Upload one or more files (optional)", 
    type=None, 
    accept_multiple_files=True
)

attachment_paths = []
if uploaded_attachments:
    for f in uploaded_attachments:
        path = os.path.join(".", f.name)
        with open(path, "wb") as out_file:
            out_file.write(f.getbuffer())
        attachment_paths.append(path)
    st.success(f"📎 {len(attachment_paths)} attachment(s) ready.")


# -------------------------------------------------------------
# 📝 SECTION 4 – Compose Email
# -------------------------------------------------------------
st.subheader("📝 Write Your Email")

subject = st.text_input("📌 Subject")
body = st.text_area("💬 Body (Use {{name}} to automatically insert recipient name)")

# -------------------------------------------------------------
# 📧 Email Function
# -------------------------------------------------------------
def create_message(sender, to, subject, body_text, attachments=None):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))

    # Attach files
    if attachments:
        for path in attachments:
            part = MIMEBase('application', 'octet-stream')
            with open(path, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
            msg.attach(part)
    return msg


def send_smtp_email(sender_email, password, to_email, subject, body, attachments=None):
    try:
        msg = create_message(sender_email, to_email, subject, body, attachments)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return "✅ Sent Successfully"
    except Exception as e:
        return f"❌ Error: {e}"


# -------------------------------------------------------------
# 🚀 SECTION 5 – SEND EMAILS
# -------------------------------------------------------------
if st.button("🚀 Send Emails"):
    if contacts is None:
        st.warning("Please upload contacts.csv first!")
    elif not subject or not body:
        st.warning("Please fill Subject and Body!")
    else:
        st.info("Sending emails... Please wait.")
        logs = []
        progress = st.progress(0)
        total = len(contacts)

        for i, row in contacts.iterrows():
            personalized_body = body.replace("{{name}}", str(row["name"]))
            status = send_smtp_email(
                user_email,
                user_password,
                row["email"],
                subject,
                personalized_body,
                attachment_paths
            )
            logs.append({"email": row["email"], "status": status})
            progress.progress((i + 1) / total)

        st.success("🎉 All emails processed!")
        logs_df = pd.DataFrame(logs)
        st.dataframe(logs_df)

        logs_df.to_csv("send_log.csv", index=False)
        st.info("📁 Log saved as send_log.csv")

# -------------------------------------------------------------
# Footer
# -------------------------------------------------------------
st.markdown("---")
st.markdown("💡 **Developed by Nabeel** | Built with ❤️ using Streamlit + Gmail SMTP")
