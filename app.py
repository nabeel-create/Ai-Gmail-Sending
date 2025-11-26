# ================================================
# 📧 AI Gmail Sender – Auto Subject & Body + Model Selection
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
for key in ["logged_in", "sender_email", "sender_password", "show_welcome",
            "generated_body", "generated_subject", "selected_model_name"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "key" in key else False

# ------------------------
# AI MODELS
# ------------------------
MODELS = {
    "Meta Llama 3.3 70B Instruct": "meta-llama-3.3-70b-instruct",
    "Qwen2.5 Coder 32B": "qwen2.5-coder-32b-instruct",
    "Meta Llama 3.2 3B": "meta-llama-3.2-3b-instruct",
    "Qwen2.5 72B Instruct": "qwen2.5-72b-instruct",
    "Nous Hermes 3 405B": "nous-hermes-3-405b-instruct",
    "Mistral Nemo 12B": "mistral-nemo-12b",
    "Mistral 7B Instruct": "mistral-7b-instruct"
}

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def help_menu():
    with st.expander("⋮ How to use Gmail Login (App Password / 2FA)"):
        st.markdown("""
        **Steps to login using Gmail App Password:**
        1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
        2. Sign in with your Gmail account.
        3. Select "Mail" → "Other (Custom name)" → Generate.
        4. Copy the 16-character password into this app's password field.

        **Notes:**
        - If 2FA is enabled, App Password is required.
        - Normal Gmail password **will not work** if 2FA is enabled.
        """)

def auto_select_model(description: str) -> str:
    desc = description.lower()
    if "code" in desc:
        return "Qwen2.5 Coder 32B"
    elif len(desc) > 1000:
        return "Qwen2.5 72B Instruct"
    else:
        return "Meta Llama 3.3 70B Instruct"

def generate_email_via_openrouter(prompt, model_key):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_KEY"]  # stored in Streamlit secrets
        )
        completion = client.chat.completions.create(
            model=model_key,
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

def send_email(to, msg, sender_email, sender_password):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return "✅ Sent"
    except Exception as e:
        return f"❌ {e}"

# ------------------------
# LOGIN PAGE
# ------------------------
def login_page():
    st.markdown("<div style='max-width: 400px; margin:auto; padding:20px; background:white; border-radius:12px; box-shadow:0 0 15px rgba(0,0,0,0.15)'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png", width=80)
    st.markdown("### Sign in to continue")

    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail App Password", type="password")
    st.markdown("<a href='https://myaccount.google.com/apppasswords' target='_blank'>🔗 Create Gmail App Password</a>", unsafe_allow_html=True)
    help_menu()

    if st.button("Login"):
        if not email or not password:
            st.warning("Enter Email & App Password")
        else:
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, password)
                server.quit()
                st.session_state.logged_in = True
                st.session_state.sender_email = email
                st.session_state.sender_password = password
                st.session_state.show_welcome = True
                st.success("Login successful! Redirecting...")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# EMAIL SENDER PAGE
# ------------------------
def email_sender_page():
    if st.session_state.show_welcome:
        st.markdown("<div style='position:fixed;top:40%;left:50%;transform:translate(-50%,-50%);padding:20px 30px;background:#d93025;color:white;font-size:20px;border-radius:12px;'>🎉 Welcome!</div>", unsafe_allow_html=True)
        st.session_state.show_welcome = False

    st.sidebar.markdown("### 📧 AI Gmail Sender")
    st.sidebar.write(f"Signed in as: **{st.session_state.sender_email}**")
    help_menu()
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    st.title("📤 Send Email")

    # 1️⃣ Upload contacts CSV
    contacts_file = st.file_uploader("📁 Upload Contacts CSV (name,email)", type="csv")
    contacts = pd.read_csv(contacts_file) if contacts_file else None
    if contacts is not None:
        st.dataframe(contacts)

    # 2️⃣ Upload attachments
    files = st.file_uploader("📎 Upload attachments", accept_multiple_files=True)
    attachment_paths = []
    if files:
        for f in files:
            with open(f.name, "wb") as out:
                out.write(f.getbuffer())
            attachment_paths.append(f.name)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # 3️⃣ Email description
    description = st.text_area("📌 Enter Email Description (what the email should say)")

    # 4️⃣ Model selection (auto/manual)
    model_options = list(MODELS.keys()) + ["Auto Select Best Model"]
    selected_model_name = st.selectbox("Select AI Model", model_options)

    if selected_model_name == "Auto Select Best Model" and description:
        selected_model_name = auto_select_model(description)
        st.info(f"Auto-selected model: {selected_model_name}")
    st.session_state.selected_model_name = selected_model_name

    # 5️⃣ Auto generate button
    if st.button("🤖 Auto Generate Subject & Email"):
        if not description:
            st.warning("Enter description first!")
        else:
            prompt = f"Based on the following description, write a professional email.\n\nDescription: {description}\n\nReturn output as:\nSubject: <subject line>\nBody: <email body>"
            ai_response = generate_email_via_openrouter(prompt, MODELS[st.session_state.selected_model_name])
            if "Subject:" in ai_response and "Body:" in ai_response:
                subject_line = ai_response.split("Subject:")[1].split("Body:")[0].strip()
                email_body = ai_response.split("Body:")[1].strip()
            else:
                subject_line = "Generated Subject"
                email_body = ai_response
            st.session_state.generated_subject = subject_line
            st.session_state.generated_body = email_body

    # 6️⃣ Display Subject & Body
    subject = st.text_input("Subject", value=st.session_state.generated_subject)
    body = st.text_area("Email Body", value=st.session_state.generated_body, height=200)

    # 7️⃣ Send Emails
    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contacts first!")
        elif not subject or not body:
            st.warning("Generate email first!")
        else:
            logs = []
            for _, row in contacts.iterrows():
                text_to_send = body.replace("{{name}}", str(row.get("name", "")))
                msg = create_message(st.session_state.sender_email, row["email"], subject, text_to_send, attachment_paths)
                status = send_email(row["email"], msg, st.session_state.sender_email, st.session_state.sender_password)
                logs.append({"email": row["email"], "status": status})
            df = pd.DataFrame(logs)
            st.success("All emails processed!")
            st.dataframe(df)
            df.to_csv("send_log.csv", index=False)
            st.info("📁 Log saved as send_log.csv")

# ------------------------
# ROUTER
# ------------------------
if not st.session_state.logged_in:
    login_page()
else:
    email_sender_page()
