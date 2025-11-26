# ================================================
# 📧 AI Gmail Sender – With Free AI Email Writer
# Author: Nabeel (Upgraded by ChatGPT)
# ================================================

import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import requests   # <-- Needed for AI writer (free)

# ------------------------
# FREE AI EMAIL GENERATOR
# ------------------------

HF_MODEL = "google/gemma-2-2b-it"     # Free model
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def generate_email(prompt):
    """Free AI email generator (HuggingFace, no key needed)"""
    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200}
        }
        response = requests.post(HF_API_URL, json=payload)
        data = response.json()

        # model returns a list with "generated_text"
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            return "Error: AI model limit reached or busy. Please try again."
    except Exception as e:
        return f"AI Error: {e}"


# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="wide")

# ------------------------
# SESSION STATE INIT
# ------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "sender_email" not in st.session_state:
    st.session_state.sender_email = ""
if "sender_password" not in st.session_state:
    st.session_state.sender_password = ""
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False

# ------------------------
# (CSS — same as your version)
# ------------------------
# ... KEEP YOUR CSS HERE ...


# ------------------------
# LOGIN PAGE (no change)
# ------------------------
def login_page():
    # (keep your full login code unchanged)
    ...
    # do not modify your login block


# ------------------------
# EMAIL SENDER PAGE (AI ADDED)
# ------------------------
def email_sender_page():

    st.title("📤 Send Email with AI Writer")

    # Upload contacts
    contacts_file = st.file_uploader("📁 Upload Contacts CSV (name,email)", type="csv")
    contacts = pd.read_csv(contacts_file) if contacts_file else None
    if contacts is not None:
        st.dataframe(contacts)

    # Attachments
    files = st.file_uploader("📎 Upload attachments", accept_multiple_files=True)
    attachment_paths = []
    if files:
        for f in files:
            with open(f.name, "wb") as out:
                out.write(f.getbuffer())
            attachment_paths.append(f.name)

    # -----------------------------
    # ---- AI EMAIL WRITER UI -----
    # -----------------------------
    st.subheader("🤖 Auto-Write Email with AI (Free)")

    topic = st.text_input("What is the email about?")
    tone = st.selectbox("Choose tone", ["Formal", "Friendly", "Professional", "Soft", "Strict", "Marketing"])

    if st.button("✨ Generate Email Automatically"):
        if not topic:
            st.warning("Please enter topic.")
        else:
            full_prompt = f"Write a {tone} email about: {topic}. Include greeting and closing."
            ai_text = generate_email(full_prompt)
            st.session_state.generated_email = ai_text
            st.success("AI Email Generated!")

    # -----------------------------
    # Email compose area (AI fills it automatically)
    # -----------------------------
    subject = st.text_input("Subject")

    body = st.text_area(
        "Body (editable)",
        value=st.session_state.get("generated_email", "")
    )

    # Send email functions (your original)
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

    # Send button
    if st.button("🚀 Send Emails"):
        if contacts is None:
            st.warning("Upload contact list first!")
        elif not subject or not body:
            st.warning("Fill all fields!")
        else:
            logs = []
            for _, row in contacts.iterrows():
                text = body.replace("{{name}}", str(row["name"]))
                msg = create_message(st.session_state.sender_email, row["email"], subject, text, attachment_paths)
                status = send_email(row["email"], msg)
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
