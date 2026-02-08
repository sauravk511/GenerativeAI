# """
# Streamlit Authentication Application
# Secure authentication system with OTP verification and password-based login.
# """

# import streamlit as st
# import auth
# import db


# # Page configuration
# st.set_page_config(
#     page_title="Secure Authentication System",
#     page_icon="🔐",
#     layout="centered",
#     initial_sidebar_state="collapsed"
# )

# # Custom CSS for better UI
# st.markdown("""
# <style>
#     .main-header {
#         text-align: center;
#         color: #1f77b4;
#         padding: 1rem 0;
#     }
#     .success-box {
#         padding: 1rem;
#         background-color: #d4edda;
#         border: 1px solid #c3e6cb;
#         border-radius: 0.25rem;
#         color: #155724;
#         margin: 1rem 0;
#     }
#     .error-box {
#         padding: 1rem;
#         background-color: #f8d7da;
#         border: 1px solid #f5c6cb;
#         border-radius: 0.25rem;
#         color: #721c24;
#         margin: 1rem 0;
#     }
#     .info-box {
#         padding: 1rem;
#         background-color: #d1ecf1;
#         border: 1px solid #bee5eb;
#         border-radius: 0.25rem;
#         color: #0c5460;
#         margin: 1rem 0;
#     }
#     .stButton>button {
#         width: 100%;
#     }
# </style>
# """, unsafe_allow_html=True)


# def show_registration_page():
#     """Display registration page with OTP verification."""
#     st.markdown("<h1 class='main-header'>🔐 Create Account</h1>", unsafe_allow_html=True)
    
#     # Check if OTP has been requested
#     if not st.session_state.otp_requested:
#         # Step 1: Request OTP
#         st.markdown("### Step 1: Enter Your Phone Number")
        
#         phone = st.text_input(
#             "Phone Number",
#             placeholder="+1234567890",
#             help="Enter your phone number (10-15 digits, optional + prefix)"
#         )
        
#         if st.button("Send OTP", type="primary"):
#             if phone:
#                 success, message = auth.request_otp(phone)
#                 if success:
#                     st.session_state.otp_requested = True
#                     st.session_state.registration_phone = phone
#                     st.success(message)
#                     st.rerun()
#                 else:
#                     st.error(message)
#             else:
#                 st.error("Please enter a phone number")
        
#         st.markdown("---")
#         st.markdown("Already have an account?")
#         if st.button("Go to Login"):
#             st.session_state.page = 'login'
#             st.rerun()
    
#     else:
#         # Step 2: Verify OTP and create password
#         st.markdown(f"### Step 2: Verify OTP for {st.session_state.registration_phone}")
        
#         st.markdown(
#             "<div class='info-box'>📱 Check your console/terminal for the OTP</div>",
#             unsafe_allow_html=True
#         )
        
#         otp = st.text_input(
#             "Enter OTP",
#             max_chars=6,
#             placeholder="123456",
#             help="Enter the 6-digit OTP sent to your phone"
#         )
        
#         password = st.text_input(
#             "Create Password",
#             type="password",
#             help="Minimum 6 characters"
#         )
        
#         password_confirm = st.text_input(
#             "Confirm Password",
#             type="password"
#         )
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             if st.button("Verify & Register", type="primary"):
#                 if not otp:
#                     st.error("Please enter OTP")
#                 elif not password:
#                     st.error("Please create a password")
#                 elif password != password_confirm:
#                     st.error("Passwords do not match")
#                 else:
#                     success, message = auth.verify_otp_and_create_user(
#                         st.session_state.registration_phone,
#                         otp,
#                         password
#                     )
#                     if success:
#                         st.success(message)
#                         st.session_state.otp_requested = False
#                         st.session_state.registration_phone = None
#                         st.session_state.page = 'login'
#                         st.balloons()
#                         st.rerun()
#                     else:
#                         st.error(message)
        
#         with col2:
#             if st.button("Cancel"):
#                 st.session_state.otp_requested = False
#                 st.session_state.registration_phone = None
#                 st.rerun()


# def show_login_page():
#     """Display login page."""
#     st.markdown("<h1 class='main-header'>🔐 Login</h1>", unsafe_allow_html=True)
    
#     phone = st.text_input(
#         "Phone Number",
#         placeholder="+1234567890",
#         help="Enter your registered phone number"
#     )
    
#     password = st.text_input(
#         "Password",
#         type="password",
#         help="Enter your password"
#     )
    
#     if st.button("Login", type="primary"):
#         if not phone:
#             st.error("Please enter your phone number")
#         elif not password:
#             st.error("Please enter your password")
#         else:
#             success, message, user = auth.login(phone, password)
#             if success:
#                 auth.create_session(user)
#                 st.success(message)
#                 st.rerun()
#             else:
#                 st.error(message)
    
#     st.markdown("---")
#     st.markdown("Don't have an account?")
#     if st.button("Create Account"):
#         st.session_state.page = 'register'
#         st.rerun()


# def show_dashboard():
#     """Display user dashboard."""
#     if not auth.is_authenticated():
#         st.session_state.page = 'login'
#         st.rerun()
#         return
    
#     user = auth.get_current_user()
    
#     st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)
    
#     st.markdown(
#         f"<div class='success-box'>✅ Welcome, {user['phone']}!</div>",
#         unsafe_allow_html=True
#     )
    
#     # User information
#     st.markdown("### Your Account Details")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.metric("Phone Number", user['phone'])
    
#     with col2:
#         st.metric("Account Status", "✅ Verified" if user['verified'] else "⚠️ Not Verified")
    
#     st.markdown(f"**Account Created:** {user['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    
#     st.markdown("---")
    
#     # Logout button
#     if st.button("🚪 Logout", type="primary"):
#         auth.logout()
#         st.success("Logged out successfully")
#         st.rerun()


# def main():
#     """Main application entry point."""
#     # Initialize session state
#     auth.init_session_state()
    
#     # Initialize database (create tables if they don't exist)
#     try:
#         db.init_database()
#     except Exception as e:
#         st.error(f"❌ Database initialization failed: {e}")
#         st.info("Please ensure PostgreSQL is running and .env file is configured correctly.")
#         st.stop()
    
#     # Route to appropriate page
#     if auth.is_authenticated():
#         show_dashboard()
#     elif st.session_state.page == 'register':
#         show_registration_page()
#     else:
#         show_login_page()


# if __name__ == "__main__":
#     main()




"""
Streamlit Authentication Application
Secure authentication system with OTP verification and password-based login.
"""

import streamlit as st
import auth
import db

# Page configuration
st.set_page_config(
    page_title="Secure Authentication System",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def show_registration_page():
    """Display registration page with OTP verification."""
    st.markdown("<h1 class='main-header'>🔐 Create Account</h1>", unsafe_allow_html=True)

    if not st.session_state.otp_requested:
        # Step 1: Request OTP
        st.markdown("### Step 1: Enter Your Phone Number or Email")
        identifier = st.text_input(
            "Phone Number or Email",
            placeholder="+1234567890 or email@example.com",
            help="Enter your phone number or Gmail to register"
        )

        if st.button("Send OTP", type="primary"):
            if identifier:
                success, message = auth.request_otp(identifier)
                if success:
                    st.session_state.otp_requested = True
                    st.session_state.registration_identifier = identifier
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a phone number or email")

        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Go to Login"):
            st.session_state.page = 'login'
            st.rerun()

    else:
        # Step 2: Verify OTP and create password
        st.markdown(f"### Step 2: Verify OTP for {st.session_state.registration_identifier}")
        st.markdown(
            "<div class='info-box'>📱 Check your console (for phone OTP) or your email</div>",
            unsafe_allow_html=True
        )

        otp = st.text_input(
            "Enter OTP",
            max_chars=6,
            placeholder="123456",
            help="Enter the 6-digit OTP sent to your phone or email"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            help="Minimum 6 characters"
        )

        password_confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Verify & Register", type="primary"):
                if not otp:
                    st.error("Please enter OTP")
                elif not password:
                    st.error("Please create a password")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.verify_otp_and_create_user(
                        st.session_state.registration_identifier,
                        otp,
                        password
                    )
                    if success:
                        st.success(message)
                        st.session_state.otp_requested = False
                        st.session_state.registration_identifier = None
                        st.session_state.page = 'login'
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)

        with col2:
            if st.button("Cancel"):
                st.session_state.otp_requested = False
                st.session_state.registration_identifier = None
                st.rerun()


def show_login_page():
    """Display login page."""
    st.markdown("<h1 class='main-header'>🔐 Login</h1>", unsafe_allow_html=True)

    identifier = st.text_input(
        "Phone Number or Email",
        placeholder="+1234567890 or email@example.com",
        help="Enter your registered phone number or email"
    )

    password = st.text_input(
        "Password",
        type="password",
        help="Enter your password"
    )

    if st.button("Login", type="primary"):
        if not identifier:
            st.error("Please enter your phone number or email")
        elif not password:
            st.error("Please enter your password")
        else:
            success, message, user = auth.login(identifier, password)
            if success:
                auth.create_session(user)
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("Create Account"):
        st.session_state.page = 'register'
        st.rerun()


def show_dashboard():
    """Display user dashboard."""
    if not auth.is_authenticated():
        st.session_state.page = 'login'
        st.rerun()
        return

    user = auth.get_current_user()

    st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='success-box'>✅ Welcome, {user['phone'] or user['email']}!</div>",
        unsafe_allow_html=True
    )

    st.markdown("### Your Account Details")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Phone Number", user['phone'] or "N/A")
        st.metric("Email", user['email'] or "N/A")
    with col2:
        st.metric("Account Status", "✅ Verified" if user['verified'] else "⚠️ Not Verified")
    st.markdown(f"**Account Created:** {user['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    if st.button("🚪 Logout", type="primary"):
        auth.logout()
        st.success("Logged out successfully")
        st.rerun()


def main():
    """Main application entry point."""
    auth.init_session_state()
    try:
        db.init_database()
    except Exception as e:
        st.error(f"❌ Database initialization failed: {e}")
        st.info("Please ensure database is running and configured correctly.")
        st.stop()

    if auth.is_authenticated():
        show_dashboard()
    elif st.session_state.page == 'register':
        show_registration_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()


