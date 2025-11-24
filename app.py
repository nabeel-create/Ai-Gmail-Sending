# =====================================================
# 📧 AI Gmail Sender – Gmail Theme (Red & White)
# Author: Nabeel
# =====================================================

import streamlit as st
import time

# -----------------------------
# Session Initialization
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False


# -----------------------------
#   TOP-RIGHT MENU (3 DOTS)
# -----------------------------
def top_right_menu():
    menu_css = """
        <style>
        .menu-dots {
            position: fixed;
            top: 15px;
            right: 25px;
            font-size: 26px;
            cursor: pointer;
            color: #D93025;
            z-index: 999;
        }
        .menu-box {
            position: fixed;
            top: 55px;
            right: 25px;
            background: white;
            padding: 15px;
            width: 260px;
            border-radius: 10px;
            border: 1px solid #ddd;
            box-shadow: 0px 4px 16px rgba(0,0,0,0.15);
            z-index: 999;
        }
        </style>
    """
    st.markdown(menu_css, unsafe_allow_html=True)

    if "menu_open" not in st.session_state:
        st.session_state.menu_open = False

    dots = st.markdown('<div class="menu-dots">⋮</div>', unsafe_allow_html=True)

    # Toggle button (invisible)
    dots_clicked = st.button(" ", key="menu_toggle_btn")
    if dots_clicked:
        st.session_state.menu_open = not st.session_state.menu_open

    if st.session_state.menu_open:
        st.markdown("""
            <div class="menu-box">
                <h4>📘 How to Use Gmail Login</h4>
                <p>If your Gmail account uses 2-Factor Authentication, you MUST use an <b>App Password</b>.</p>

                <p><b>Steps:</b></p>
                <ol>
                    <li>Open Google Account</li>
                    <li>Go to: Security → App Passwords</li>
                    <li>Select: Mail + Windows</li>
                    <li>Copy the 16-digit password</li>
                    <li>Use it here instead of your actual Gmail password</li>
                </ol>

                <a href="https://myaccount.google.com/apppasswords" target="_blank">
                    🔗 Open Google App Passwords
                </a>
            </div>
        """, unsafe_allow_html=True)


# -----------------------------
#   LOGIN PAGE UI
# -----------------------------
def login_page():

    st.set_page_config(page_title="Gmail Login", layout="centered")

    page_css = """
        <style>
            body {
                background: #fceeee;
            }
            .login-box {
                margin-top: 90px;
                background: white;
                padding: 40px 50px;
                border-radius: 18px;
                width: 420px;
                margin-left: auto;
                margin-right: auto;
                box-shadow: 0px 6px 25px rgba(0, 0, 0, 0.15);
                border-top: 6px solid #D93025;
            }
            .title {
                font-size: 32px;
                text-align: center;
                color: #D93025;
                font-weight: 700;
                margin-bottom: 10px;
            }
        </style>
    """
    st.markdown(page_css, unsafe_allow_html=True)

    top_right_menu()

    # UI Box
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        st.markdown("<div class='title'>Gmail Login</div>", unsafe_allow_html=True)

        email = st.text_input("Gmail Address")
        pwd = st.text_input("Password / App Password", type="password")

        login_btn = st.button("Login", use_container_width=True)

        if login_btn:
            if email.strip() == "" or pwd.strip() == "":
                st.error("Please fill all fields.")
            else:
                st.session_state.logged_in = True
                st.session_state.show_welcome = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
#   WELCOME POPUP
# -----------------------------
def welcome_popup():
    popup_css = """
        <style>
            .welcome-msg {
                position: fixed;
                top: 45%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 25px 40px;
                border-radius: 16px;
                border-left: 7px solid #D93025;
                box-shadow: 0px 8px 25px rgba(0,0,0,0.18);
                font-size: 22px;
                font-weight: 600;
                z-index: 9999;
                color: #D93025;
                text-align: center;
            }
        </style>
    """
    st.markdown(popup_css, unsafe_allow_html=True)
    st.markdown('<div class="welcome-msg">🎉 Welcome Back!</div>', unsafe_allow_html=True)

    time.sleep(2)
    st.session_state.show_welcome = False
    st.rerun()


# -----------------------------
#   MAIN APP PAGE
# -----------------------------
def app_page():

    st.title("📨 Gmail Sender Dashboard")
    st.write("This is your main Gmail automation dashboard interface.")


# -----------------------------
#   ROUTING
# -----------------------------
if not st.session_state.logged_in:
    login_page()

else:
    if st.session_state.show_welcome:
        welcome_popup()

    top_right_menu()
    app_page()
