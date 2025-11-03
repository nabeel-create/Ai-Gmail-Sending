# ============================
# 📧 AI Gmail Sender App
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from openai import OpenAI

# ============================
# 🔒 Load Secrets from Streamlit
# ============================

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REFRESH_TOKEN = st.secrets["REFRESH_TOKEN"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ============================
# 🎨 Streamlit Page Setup
# ============================

st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="centered")
st.title("📨 AI Gmail Sender by Nabeel")
st.write("Generate and send professional AI-written emails using Gmail API and OpenAI GPT-5 ✨")

# ============================
# 🧠 AI Email Generator
# ============================

st.subheader("✍️ Generate Email with AI")

subject_prompt = st.text_input("Enter email subject or topic")
body_prompt = st.text_area("Describe what you want to say in the email")

if st.button("✨ Generate Email"):
    if not body_prompt.strip():
        st.warning("Please enter a topic or message idea.")
    else:
        with st.spinner("AI is crafting your email..."):
            try:
                ai_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional email writer."},
                        {"role": "user", "content": f"Write a formal and concise email about: {body_prompt}"}
                    ],
                    max_tokens=300
                )
                ai_text = ai_response.choices[0].message.content.strip()
                st.success("✅ Email generated successfully!")
                st.text_area("📄 AI Generated Email", ai_text, height=250)
            except Exception as e:
                st.error(f"AI generation failed: {str(e)}")

# ============================
# 📤 Gmail Sending Section
# ============================

st.subheader("📩 Send Email")

sender_email = st.text_input("Your Gmail address")
to_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject")
body = st.text_area("Email Body")

if st.button("📬 Send Email"):
    if not all([sender_email, to_email, subject, body]):
        st.warning("⚠️ Please fill in all fields before sending.")
    else:
        try:
            creds = Credentials(
                None,
                refresh_token=REFRESH_TOKEN,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token"
            )
            service = build('gmail', 'v1', credentials=creds)

            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = sender_email
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}

            sent = service.users().messages().send(userId="me", body=send_message).execute()
            st.success(f"✅ Email sent successfully to {to_email}")
        except Exception as e:
            st.error(f"Error sending email: {str(e)}")

# ============================
# 📘 Footer
# ============================

st.markdown("---")
st.markdown("🧠 **Built by Nabeel** | Powered by Gmail API + OpenAI GPT-5 ✨")

