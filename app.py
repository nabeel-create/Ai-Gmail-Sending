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
import streamlit as st

def login_page():
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    # --------------------
    # CUSTOM CSS
    # --------------------
    st.markdown("""
    <style>
        /* BODY BACKGROUND */
        body {
            background: linear-gradient(135deg, #e3f2fd, #fce4ec);
            font-family: 'Segoe UI', sans-serif;
        }

        /* HEADER */
        .header {
            background: linear-gradient(90deg, #1a73e8, #d81b60);
            padding: 25px;
            border-radius: 0 0 18px 18px;
            text-align: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }

        /* LOGIN CARD */
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 18px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.10);
            width: 380px;
            margin: auto;
            position: relative;
            top: 50%;
            transform: translateY(-50%);
        }

        .title {
            font-size: 24px;
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

        /* INPUT FIELDS */
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            font-size: 14px;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #1a73e8;
            outline: none;
            box-shadow: 0 0 5px rgba(26,115,232,0.5);
        }

        /* BUTTON */
        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg, #1a73e8, #6a1b9a);
            color: white;
            padding: 10px;
            border-radius: 10px;
            border: none;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #1565c0, #4a148c);
        }

        /* FORGOT PASSWORD LINK */
        .forgot {
            text-align: center;
            font-size: 13px;
            margin-top: 10px;
        }
        .forgot a {
            color: #1a73e8;
            text-decoration: none;
        }
        .forgot a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

    # --------------------
    # HEADER
    # --------------------
    st.markdown("<div class='header'>Gmail Login</div>", unsafe_allow_html=True)

    # --------------------
    # LOGIN CARD
    # --------------------
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Sign In</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Use your Gmail and App Password</div>", unsafe_allow_html=True)

    email = st.text_input("Gmail Address", placeholder="example@gmail.com")
    password = st.text_input("Password / App Password", type="password", placeholder="Enter your Gmail password")

    login_clicked = st.button("Login")

    st.markdown('<div class="forgot"><a href="#">Forgot Password?</a></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------
    # LOGIN LOGIC
    # --------------------
    if login_clicked:
        if email.strip() == "" or password.strip() == "":
            st.error("Please enter both email and password.")
        else:
            st.success("Login successful!")
            st.session_state['logged_in'] = True
            st.session_state['email'] = email

# Run login page if user not logged in
if 'logged_in' not in st.session_state:
    login_page()



# --------------------------
# APP FLOW CONTROLLER
# --------------------------
if not st.session_state.logged_in:
    login_page()
else:
    app_page()
