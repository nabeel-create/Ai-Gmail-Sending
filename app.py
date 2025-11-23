# ============================
# 📧 AI Gmail Sender – Beautiful Login + Full App
# Author: Nabeel
# ============================

import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(page_title="AI Gmail Sender", page_icon="📧", layout="centered")

# --------------------------
# SESSION STATE FOR LOGIN
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------
# BEAUTIFUL LOGIN PAGE
# --------------------------
def login_page():
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    # Custom CSS for beautiful UI
    st.markdown("""
        <style>
            body {
                background: #f5f7fa;
            }
            .login-card {
                background: white;
                padding: 40px;
                border-radius: 18px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.07);
                width: 380px;
                margin: auto;
                margin-top: 90px;
            }
            .title {
                font-size: 26px;
                font-weight: 700;
                text-align: center;
                color: #333;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-bottom: 25px;
            }
            .stButton>button {
                width: 100%;
                background: #1a73e8;
                color: white;
                padding: 10px;
                border-radius: 10px;
                border: none;
                font-size: 16px;
            }
            .stButton>button:hover {
                background: #1567d5;
            }
            .link {
                text-align: center;
                margin-top: 15px;
            }
            .link a {
                color: #1a73e8;
                text-decoration: none;
                font-size: 14px;
            }
            .link a:hover {
                text-decoration: underline;
            }
        </style>
    """, unsafe_allow_html=True)

    # Login Card Start
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>Sign in to Continue</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Use your Gmail and App Password</div>", unsafe_allow_html=True)

    # Input Fields
    email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    password = st.text_input("Password / App Password", type="password", placeholder="Enter your Gmail App Password")

    # Login Button
    login_clicked = st.button("Login")

    # App Password Info
    st.markdown("""
        <div class='link'>
            Need help generating an App Password? 
            <a href='https://support.google.com/accounts/answer/185833?hl=en' target='_blank'>Click here</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    # Login Card End

    # Simple login validation
    if login_clicked:
        if email.strip() == "" or password.strip() == "":
            st.error("Please enter both email and password.")
        else:
            st.success("Login successful!")
            st.session_state['logged_in'] = True
            st.session_state['email'] = email

# --------------------------
# APP PAGE PLACEHOLDER
# --------------------------
def app_page():
    st.title("Welcome to AI Gmail Sender")
    st.write("You are logged in as:", st.session_state.get("email"))

# --------------------------
# APP FLOW CONTROLLER
# --------------------------
if not st.session_state.logged_in:
    login_page()
else:
    app_page()
