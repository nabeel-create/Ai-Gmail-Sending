# ======================================
# 📧 AI Gmail Sender – Premium Edition
# Author: Nabeel
# ======================================

import streamlit as st
import pandas as pd
import os, json, smtplib, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --------------------------------------
# PAGE CONFIG
# --------------------------------------
st.set_page_config(
    page_title="AI Gmail Sender",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------
# CUSTOM CSS THEME (Purple Gradient)
# --------------------------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #6a0dad, #c850c0, #ff6fd8);
        background-attachment: fixed;
    }

    .main {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 20px;
    }

    .stButton>button {
        border-radius: 10px;
        padding: 10px 20px;
        background-color:#8e2de2;
        color:white;
        font-size:16px;
        border:none;
    }
    .stButton>button:hover {
        background-color:#a445f7;
    }

    .gradient-box {
        padding:20px;
        border-radius:15px;
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(14px);
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------
# DARK MODE
# --------------------------------------
dark = st.sidebar.toggle("🌙 Dark Mode")
if dark:
    st.markdown("""
        <style>
        body { background: #0d0f14 !important; }
        .main { background: rgba(255,255,255,0.07); }
        .stTextInput>div>div>input, textarea { color:white !important; }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------
# SIDEBAR MENU
# --------------------------------------
st.sidebar.title("📧 AI Gmail Sender")
menu = st.sidebar.radio(
    "Menu",
    ["📖 Instructions", "🔑 Login", "📁 Contacts", "📝 Email", "📎 Attachments", "📑 Templates", "🚀 Send"]
)

st.sidebar.markdown("----")
st.sidebar.info("💜 Developed by Nabeel")

# --------------------------------------
# TEMPLATES LOADING
# --------------------------------------
TEMPLATE_FILE = "template.json"

def load_template():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    return {"subject":"", "body":""}

def save_template(subject, body):
    with open(TEMPLATE_FILE, "w") as f:
        json.dump({"subject": subject, "body": body}, f)

template = load_template()


# --------------------------------------
# PAGE 1 – INSTRUCTIONS
# --------------------------------------
if menu == "📖 Instructions":
    st.title("📘 How to Use AI Gmail Sender")

    st.markdown("""
    ### 🔑 Step 1 — Create Gmail App Password  
    Gmail blocks normal login for apps.  
    You **must** create an App Password.

    👉 Create here: **https://myaccount.google.com/apppasswords**

    ---

    ### 📁 Step 2 — Upload Contacts  
    CSV must include:

    - name  
    - email  

    ---

    ### 📝 Step 3 — Write Email  
    Use **{{name}}** to personalize each message.

    ---

    ### 📎 Step 4 — Attach Files (Optional)

    ---

    ### 🚀 Step 5 — Send Emails  
    Each message will be personalized and logged.
    """)

# --------------------------------------
# PAGE 2 – LOGIN
# --------------------------------------
if menu == "🔑 Login":
    st.title("🔑 Gmail Login")

    with st.container():
        st.markdown("### Enter Gmail Credentials")
        st.info("Use Gmail + App Password")

        user_email = st.text_input("Your Gmail:")
        user_pass = st.text_input("App Password:", type="password")

# --------------------------------------
# PAGE 3 – CONTACTS
# --------------------------------------
if menu == "📁 Contacts":
    st.title("📁 Upload Contacts")

    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        st.session_state["contacts"] = pd.read_csv(uploaded)
        st.dataframe(st.session_state["contacts"])
        st.success("Contacts loaded!")

# --------------------------------------
# PAGE 4 – EMAIL
# --------------------------------------
if menu == "📝 Email":
    st.title("📝 Compose Email")

    col1, col2 = st.columns(2)

    with col1:
        subject = st.text_input("Subject", value=template["subject"])

    with col2:
        if st.button("💾 Save as Template"):
            save_template(subject, template["body"])
            st.success("Saved!")

    body = st.text_area("Message Body (Use {{name}})", height=300, value=template["body"])

    if st.button("Save Full Draft"):
        save_template(subject, body)
        st.success("Draft Saved!")

# --------------------------------------
# PAGE 5 – ATTACHMENTS
# --------------------------------------
if menu == "📎 Attachments":
    st.title("📎 Attach Files")

    files = st.file_uploader("Upload Files", accept_multiple_files=True)
    paths = []

    if files:
        for f in files:
            p = os.path.join(".", f.name)
            with open(p, "wb") as out:
                out.write(f.getbuffer())
            paths.append(p)

        st.session_state["attach"] = paths
        st.success(f"{len(paths)} attachment(s) added!")

# --------------------------------------
# PAGE 6 – TEMPLATES
# --------------------------------------
if menu == "📑 Templates":
    st.title("📑 Saved Templates")

    st.write("Subject:", template["subject"])
    st.write("Body:")
    st.code(template["body"])

    if st.button("Clear Template"):
        save_template("", "")
        st.warning("Template cleared!")

# --------------------------------------
# PAGE 7 – SEND EMAILS
# --------------------------------------
if menu == "🚀 Send":
    st.title("🚀 Send Emails")

    if st.button("📧 Send Test Email"):
        try:
            msg = MIMEText("This is a test email from AI Gmail Sender.")
            msg["Subject"] = "Test Email"
            msg["From"] = user_email
            msg["To"] = user_email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(user_email, user_pass)
                server.sendmail(user_email, user_email, msg.as_string())

            st.success("Test email sent!")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🚀 Send to Contacts"):
        contacts = st.session_state.get("contacts")
        attachments = st.session_state.get("attach", [])

        if contacts is None:
            st.error("Upload contacts first!")
        else:
            st.info("Sending... Please wait...")
            my_bar = st.progress(0)

            log = []

            for i, row in contacts.iterrows():
                try:
                    msg = MIMEMultipart()
                    msg["From"] = user_email
                    msg["To"] = row["email"]
                    msg["Subject"] = subject

                    personalized = body.replace("{{name}}", str(row["name"]))
                    msg.attach(MIMEText(personalized, "plain"))

                    # Attach files
                    for p in attachments:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(open(p, "rb").read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(p)}")
                        msg.attach(part)

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(user_email, user_pass)
                        server.sendmail(user_email, row["email"], msg.as_string())

                    status = "Sent"
                except Exception as e:
                    status = f"Failed: {e}"

                log.append({"email": row["email"], "status": status})
                my_bar.progress((i + 1) / len(contacts))
                time.sleep(0.3)

            st.success("🎉 All emails processed!")
            st.dataframe(pd.DataFrame(log))
