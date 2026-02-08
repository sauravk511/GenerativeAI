# """
# Authentication logic module.
# Handles user registration, login, and session management.
# """

# import bcrypt
# import re
# import streamlit as st
# from config import Config
# import db
# import otp as otp_module


# def validate_phone(phone: str):
#     """
#     Validate phone number format.
    
#     Args:
#         phone: Phone number to validate
        
#     Returns:
#         Tuple of (is_valid, error_message)
#     """
#     # Remove spaces and special characters
#     phone = phone.strip()
    
#     # Basic validation: 10-15 digits
#     if not phone:
#         return False, "Phone number is required"
    
#     # Check if contains only digits and optional + at start
#     if not re.match(r'^\+?\d{10,15}$', phone):
#         return False, "Phone number must be 10-15 digits (optional + prefix)"
    
#     return True, ""


# def validate_password(password: str):
#     """
#     Validate password strength.
    
#     Args:
#         password: Password to validate
        
#     Returns:
#         Tuple of (is_valid, error_message)
#     """
#     if not password:
#         return False, "Password is required"
    
#     if len(password) < 6:
#         return False, "Password must be at least 6 characters"
    
#     if len(password) > 128:
#         return False, "Password must be less than 128 characters"
    
#     return True, ""


# def hash_password(password: str):
#     """
#     Hash a password using bcrypt.
    
#     Args:
#         password: Plain text password
        
#     Returns:
#         Hashed password as string
#     """
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)).decode('utf-8')


# def verify_password(password: str, password_hash: str):
#     """
#     Verify a password against a hash.
    
#     Args:
#         password: Plain text password
#         password_hash: Stored password hash
        
#     Returns:
#         True if password matches, False otherwise
#     """
#     try:
#         return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
#     except Exception as e:
#         print(f"[ERROR] Password verification error: {e}")
#         return False


# def request_otp(phone: str):
#     """
#     Request OTP for phone number.
    
#     Args:
#         phone: Phone number
        
#     Returns:
#         Tuple of (success, message)
#     """
#     # Validate phone
#     is_valid, error = validate_phone(phone)
#     if not is_valid:
#         return False, error
    
#     # Check if user already exists
#     if db.user_exists(phone):
#         return False, "Account already exists. Please login."
    
#     # Send OTP
#     if otp_module.send_otp(phone):
#         return True, f"OTP sent to {phone}. Check your console/terminal."
#     else:
#         return False, "Failed to send OTP. Please try again."


# def verify_otp_and_create_user(phone: str, otp: str, password: str):
#     """
#     Verify OTP and create user account.
    
#     Args:
#         phone: Phone number
#         otp: OTP to verify
#         password: User's chosen password
        
#     Returns:
#         Tuple of (success, message)
#     """
#     # Validate inputs
#     is_valid, error = validate_phone(phone)
#     if not is_valid:
#         return False, error
    
#     is_valid, error = validate_password(password)
#     if not is_valid:
#         return False, error
    
#     # Verify OTP
#     if not otp_module.verify_otp(phone, otp):
#         return False, "Invalid or expired OTP"
    
#     # Check if user already exists (double-check)
#     if db.user_exists(phone):
#         return False, "Account already exists"
    
#     # Hash password and create user
#     password_hash = hash_password(password)
#     user_id = db.create_user(phone, password_hash)
    
#     if user_id:
#         return True, "Account created successfully! Please login."
#     else:
#         return False, "Failed to create account. Please try again."


# def login(phone: str, password: str):
#     """
#     Authenticate user with phone and password.
    
#     Args:
#         phone: Phone number
#         password: Password
        
#     Returns:
#         Tuple of (success, message, user_data)
#     """
#     # Validate inputs
#     is_valid, error = validate_phone(phone)
#     if not is_valid:
#         return False, error, None
    
#     if not password:
#         return False, "Password is required", None
    
#     # Get user from database
#     user = db.get_user_by_phone(phone)
    
#     if not user:
#         return False, "Invalid phone number or password", None
    
#     # Verify password
#     if not verify_password(password, user['password_hash']):
#         return False, "Invalid phone number or password", None
    
#     # Check if user is verified
#     if not user['verified']:
#         return False, "Account not verified", None
    
#     print(f"[SUCCESS] User logged in: {phone}")
#     return True, "Login successful", user


# def init_session_state():
#     """Initialize session state variables."""
#     if 'authenticated' not in st.session_state:
#         st.session_state.authenticated = False
#     if 'user' not in st.session_state:
#         st.session_state.user = None
#     if 'page' not in st.session_state:
#         st.session_state.page = 'login'
#     if 'otp_requested' not in st.session_state:
#         st.session_state.otp_requested = False
#     if 'registration_phone' not in st.session_state:
#         st.session_state.registration_phone = None


# def is_authenticated():
#     """Check if user is authenticated."""
#     return st.session_state.get('authenticated', False)


# def get_current_user():
#     """Get current authenticated user."""
#     return st.session_state.get('user', None)


# def create_session(user):
#     """Create user session."""
#     st.session_state.authenticated = True
#     st.session_state.user = user
#     st.session_state.page = 'dashboard'


# def logout():
#     """Clear user session."""
#     st.session_state.authenticated = False
#     st.session_state.user = None
#     st.session_state.page = 'login'
#     st.session_state.otp_requested = False
#     st.session_state.registration_phone = None
#     print("[SUCCESS] User logged out")


"""
Authentication logic module.
Handles user registration, login, and session management.
"""

import bcrypt
import re
import streamlit as st
from config import Config
import db
import otp as otp_module


def validate_password(password: str):
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    return True, ""


def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)).decode('utf-8')


def verify_password(password: str, password_hash: str):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False


def request_otp(identifier: str):
    if not identifier:
        return False, "Phone number or email required"
    
    if '@' in identifier:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', identifier):
            return False, "Invalid email format"
    else:
        if not re.match(r'^\+?\d{10,15}$', identifier):
            return False, "Phone number must be 10-15 digits"
    
    if db.user_exists(identifier):
        return False, "Account already exists. Please login."
    
    if otp_module.send_otp(identifier):
        return True, f"OTP sent to {identifier}"
    return False, "Failed to send OTP"


def verify_otp_and_create_user(identifier: str, otp: str, password: str):
    if not identifier:
        return False, "Identifier required"
    if not otp:
        return False, "OTP required"
    valid, err = validate_password(password)
    if not valid:
        return False, err
    if not otp_module.verify_otp(identifier, otp):
        return False, "Invalid or expired OTP"
    if db.user_exists(identifier):
        return False, "Account already exists"
    db.create_user(identifier, hash_password(password))
    return True, "Account created successfully! Please login"


def login(identifier: str, password: str):
    if not identifier or not password:
        return False, "Identifier and password required", None
    user = db.get_user_by_identifier(identifier)
    if not user or not verify_password(password, user['password_hash']):
        return False, "Invalid identifier or password", None
    if not user['verified']:
        return False, "Account not verified", None
    return True, "Login successful", user


def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'otp_requested' not in st.session_state:
        st.session_state.otp_requested = False
    if 'registration_identifier' not in st.session_state:
        st.session_state.registration_identifier = None


def is_authenticated():
    return st.session_state.get('authenticated', False)


def get_current_user():
    return st.session_state.get('user', None)


def create_session(user):
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.page = 'dashboard'


def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = 'login'
    st.session_state.otp_requested = False
    st.session_state.registration_identifier = None
