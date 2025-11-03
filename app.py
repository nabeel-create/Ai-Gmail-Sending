# ============================
# 📧 AI Gmail Sender – Streamlit Cloud Version (Enhanced)
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import base64
import time
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Optional: OpenAI (for AI-generated email body)
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# --- Page Setup ---
st.set_page_config(page_title="AI Gmail Sender by Nabeel", page_icon="📧", layout="wide")
# CSS Styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
    }
    .card {
        background: #ffffff;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(13, 38, 76, 0.08);
        padding: 20px;
        margin-bottom: 16px;
    }
    .title {
        font-size: 28px;
        font-weight: 700;
        color: #0b63d6;
    }
    .sub {
        color: #6b7280;
        font-size: 14px;
    }
    .stButton>button {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
with st.container():
    col1, col2 = st.columns([0.12, 0.88])
    with col1:
        st.image("https://i.imgur.com/0Z8YvWi.png", width=64)  # placeholder logo; replace with your own if desired
    with col2:
        st.markdown("<div class='title'>📧 AI Gmail Sender</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>By Nabeel — Generate, personalize & send emails automatically (AI-assisted)</div>", unsafe_allow_html=True)
st.markdown("---")

# Theme toggle (simple)
theme = st.radio("🎨 Theme", ["Light", "Dark"], horizontal=True)
if theme == "Dark":
    st.markdown(
        """
        <style>
        .stApp { background-color: #0b1220; color: #e6eef8; }
        .card { background: #0f1724; box-shadow: none; }
        .title { color: #7cc3ff; }
        .sub { color: #9aa9bf; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Load secrets (Streamlit Cloud) ---
# IMPORTANT: Add CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN in Streamlit secrets
missing_secrets = []
for key in ["CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN"]:
    if key not in st.secrets:
        missing_secrets.append(key)

if missing_secrets:
    st.error(
        "Missing Streamlit secrets: "
        + ", ".join(missing_secrets)
        + ".\n\nGo to Streamlit Cloud → Manage App → Settings → Secrets and add them."
    )
    st.stop()

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REFRESH_TOKEN = st.secrets["REFRESH_TOKEN"]

# Optional OpenAI key
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", None)
if OPENAI_KEY and OPENAI_AVAILABLE:
    openai.api_key = OPENAI_KEY

# --- Helper: create Gmail service ---
def create_gmail_service(client_id, client_secret, refresh_token):
    creds_data = {
        "token": "",
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": ["https://www.googleapis.com/auth/gmail.send"],
        "type": "authorized_user",
    }
    creds = Credentials.from_authorized_user_info(creds_data)
    service = build("gmail", "v1", credentials=creds)
    return service

# Try to create service and handle errors
try:
    service = create_gmail_service(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
    st.success("✅ Gmail API connected.")
except Exception as e:
    st.error(f"Could not connect to Gmail API: {e}")
    st.stop()

# --- Left: AI generator and compose (main card) ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Email Generator (optional)")
    st.markdown("Describe the email purpose and tone; the AI will draft a message you can edit.")
    ai_prompt = st.text_area("AI prompt (e.g., 'Follow-up after meeting about product demo — friendly tone')", height=80)

    col_a1, col_a2 = st.columns([0.6, 0.4])
    with col_a1:
        ai_model = st.selectbox("AI model (if available)", ["gpt-3.5-turbo"], index=0)
    with col_a2:
        temp = st.slider("Creativity", 0.0, 1.0, 0.6)

    generate_clicked = st.button("✨ Generate Email (AI)")
    ai_generated = ""
    if generate_clicked:
        if not ai_prompt.strip():
            st.warning("Enter an AI prompt above first.")
        elif not OPENAI_KEY or not OPENAI_AVAILABLE:
            st.error("OpenAI not configured: Add OPENAI_API_KEY to Streamlit secrets and install 'openai' package.")
        else:
            try:
                with st.spinner("Generating email..."):
                    # use ChatCompletion
                    resp = openai.ChatCompletion.create(
                        model=ai_model,
                        messages=[
                            {"role": "system", "content": "You are a professional email writer. Keep it concise and friendly."},
                            {"role": "user", "content": f"Write a short professional email: {ai_prompt}"}
                        ],
                        temperature=float(temp),
                        max_tokens=400,
                    )
                    ai_generated = resp.choices[0].message["content"].strip()
                    st.success("✅ AI draft ready — edit below if you want.")
            except Exception as e:
                st.error(f"AI generation failed: {e}")

    st.markdown("### 📝 Compose / Edit Email")
    sender = st.text_input("Sender Gmail (authorized account)", value="")
    subject = st.text_input("Subject", value="")
    # If AI generated text exists, prefill body with it; else keep previous typed
    if ai_generated:
        body_default = ai_generated
    else:
        body_default = st.session_state.get("body_default", "Hello {{name}},\n\n")
    body = st.text_area("Body (use {{name}} for personalization)", value=body_default, height=240)
    st.session_state["body_default"] = body  # persist between reruns

    st.markdown("</div>", unsafe_allow_html=True)

# --- Right: Contacts, attachments, settings, send button (in a card) ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📁 Contacts & Attachments")
    st.markdown("Upload a CSV with columns: `name,email`")

    uploaded_file = st.file_uploader("Upload contacts.csv", type=["csv"])
    contacts = None
    if uploaded_file:
        try:
            contacts = pd.read_csv(uploaded_file)
            if not {"name", "email"}.issubset(set(contacts.columns.str.lower())):
                # try to normalize column names
                cols_lower = {c.lower(): c for c in contacts.columns}
                if "name" in cols_lower and "email" in cols_lower:
                    contacts = contacts.rename(columns={cols_lower["name"]: "name", cols_lower["email"]: "email"})
                else:
                    st.error("CSV must include 'name' and 'email' columns (case-insensitive).")
                    contacts = None
            if contacts is not None:
                st.dataframe(contacts.head(50))
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            contacts = None

    uploaded_attachments = st.file_uploader("Upload attachments (optional)", accept_multiple_files=True)
    attachment_paths = []
    # Save attachments to disk (ephemeral)
    if uploaded_attachments:
        for f in uploaded_attachments:
            path = os.path.join("attachments", f.name)
            os.makedirs("attachments", exist_ok=True)
            with open(path, "wb") as out_file:
                out_file.write(f.getbuffer())
            attachment_paths.append(path)
        st.write(f"✅ {len(attachment_paths)} attachment(s) ready")

    # Advanced settings
    st.markdown("---")
    st.subheader("⚙️ Settings")
    send_limit = st.number_input("Max emails to send (0 = all)", min_value=0, step=1, value=0)
    delay_between = st.number_input("Delay between sends (seconds)", min_value=0, step=1, value=1)
    preview_mode = st.checkbox("Preview first 3 personalized emails before sending", value=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Functions to create and send emails ---
def create_message(sender, to, subject, body_text, attachments=None):
    msg = MIMEMultipart()
    msg["to"] = to
    msg["from"] = sender
    msg["subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))
    if attachments:
        for path in attachments:
            try:
                part = MIMEBase("application", "octet-stream")
                with open(path, "rb") as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
                msg.attach(part)
            except Exception as e:
                st.warning(f"Attachment {path} could not be attached: {e}")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}

def send_message(service, user_id, message):
    try:
        sent = service.users().messages().send(userId=user_id, body=message).execute()
        return True, sent.get("id", "")
    except Exception as e:
        return False, str(e)

# --- Preview and Send area ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Send Emails")

    if st.button("Preview / Validate"):
        if contacts is None:
            st.warning("Upload contacts.csv first.")
        elif not sender or not subject or not body:
            st.warning("Fill sender, subject, and body.")
        else:
            preview_rows = contacts.head(3) if preview_mode else contacts.head(min(3, len(contacts)))
            preview_list = []
            for _, row in preview_rows.iterrows():
                try:
                    ptext = str(body).replace("{{name}}", str(row["name"]))
                except Exception:
                    ptext = str(body)
                preview_list.append({"email": row["email"], "preview": ptext})
            st.info("Preview of personalized emails:")
            for p in preview_list:
                st.markdown(f"**To:** {p['email']}")
                st.code(p["preview"])
    send_pressed = st.button("🚀 Send Emails Now")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Perform sending if requested ---
if send_pressed:
    if contacts is None:
        st.warning("Upload contacts.csv first.")
    elif not sender or not subject or not body:
        st.warning("Fill sender, subject, and body.")
    else:
        total = len(contacts)
        if send_limit > 0:
            total_to_send = min(send_limit, total)
        else:
            total_to_send = total

        st.info(f"Preparing to send {total_to_send} email(s).")
        progress_bar = st.progress(0)
        status_logs = []
        start_time = time.time()
        for i, (_, row) in enumerate(contacts.iterrows()):
            if i >= total_to_send:
                break
            recipient = row["email"]
            try:
                personalized = str(body).replace("{{name}}", str(row.get("name", "")))
            except Exception:
                personalized = body
            msg = create_message(sender, recipient, subject, personalized, attachments=attachment_paths)
            success, info = send_message(service, "me", msg)
            if success:
                status = f"Sent (ID: {info})"
            else:
                status = f"Error: {info}"
            status_logs.append({"index": i + 1, "email": recipient, "status": status, "subject": subject})
            progress_bar.progress((i + 1) / total_to_send)
            # optional delay
            if delay_between > 0:
                time.sleep(delay_between)

        elapsed = time.time() - start_time
        st.success(f"Finished sending {len(status_logs)} email(s) in {elapsed:.1f}s")
        st.balloons()

        # Show logs and provide download button
        logs_df = pd.DataFrame(status_logs)
        st.dataframe(logs_df)
        csv = logs_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download send_log.csv", data=csv, file_name="send_log.csv", mime="text/csv")

        # Cleanup attachments folder (optional)
        try:
            if os.path.exists("attachments"):
                for f in os.listdir("attachments"):
                    os.remove(os.path.join("attachments", f))
                os.rmdir("attachments")
        except Exception:
            pass

# Footer / help
st.markdown("---")
st.markdown(
    "💡 **Notes:**\n"
    "- Keep your Gmail credentials private (use Streamlit secrets).\n"
    "- If using OpenAI, add `OPENAI_API_KEY` in secrets and include `openai` in requirements.\n"
    "- Avoid sending large batches too quickly to prevent Gmail rate limits."
)
