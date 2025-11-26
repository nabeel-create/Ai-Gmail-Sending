# ------------------------
# LOGIN PAGE
# ------------------------
def login_page():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    # Replace logo with Gmail text
    st.markdown("<h1 style='color:#d93025; font-weight:bold; font-size:36px; margin-bottom:20px;'>Gmail</h1>", unsafe_allow_html=True)
    
    st.markdown("### Sign in to continue")

    email = st.text_input("Gmail Address")
    password = st.text_input("Gmail App Password", type="password")

    st.markdown(
        "<a href='https://myaccount.google.com/apppasswords' target='_blank'>🔗 Create Gmail App Password</a>",
        unsafe_allow_html=True
    )

    help_menu()  # show three dots help

    if st.button("Login", key="login_button"):
        if not email or not password:
            st.warning("Please enter both Email and App Password")
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
                st.rerun()

            except Exception as e:
                st.error(f"Login failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
