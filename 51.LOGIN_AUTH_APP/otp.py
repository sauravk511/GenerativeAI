# """
# OTP generation and verification module.
# Handles OTP creation, hashing, and validation.
# """

# import random
# import bcrypt
# from config import Config
# import db


# def generate_otp():
#     """
#     Generate a random 6-digit OTP.
    
#     Returns:
#         String containing 6-digit OTP
#     """
#     return str(random.randint(100000, 999999))


# def hash_otp(otp: str):
#     """
#     Hash an OTP using bcrypt.
    
#     Args:
#         otp: Plain text OTP
        
#     Returns:
#         Hashed OTP as string
#     """
#     return bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)).decode('utf-8')


# def verify_otp(phone: str, otp: str):
#     """
#     Verify an OTP against the stored hash.
    
#     Args:
#         phone: Phone number
#         otp: Plain text OTP to verify
        
#     Returns:
#         True if OTP is valid and not expired, False otherwise
#     """
#     stored_hash = db.get_otp(phone)
    
#     if not stored_hash:
#         print(f"[ERROR] No valid OTP found for {phone}")
#         return False
    
#     try:
#         is_valid = bcrypt.checkpw(otp.encode('utf-8'), stored_hash.encode('utf-8'))
        
#         if is_valid:
#             print(f"[SUCCESS] OTP verified successfully for {phone}")
#             # Delete OTP after successful verification
#             db.delete_otp(phone)
#         else:
#             print(f"[ERROR] Invalid OTP for {phone}")
        
#         return is_valid
        
#     except Exception as e:
#         print(f"[ERROR] OTP verification error: {e}")
#         return False


# def send_otp(phone: str):
#     """
#     Generate and 'send' OTP (print to console for testing).
    
#     Args:
#         phone: Phone number to send OTP to
        
#     Returns:
#         True if OTP was generated and stored successfully
#     """
#     try:
#         # Clean up expired OTPs
#         db.cleanup_expired_otps()
        
#         # Generate new OTP
#         otp = generate_otp()
        
#         # Hash and store OTP
#         otp_hash = hash_otp(otp)
#         db.store_otp(phone, otp_hash)
        
#         # Print OTP to console (simulating SMS)
#         print("\n" + "="*50)
#         print(f"[OTP] OTP for {phone}: {otp}")
#         print(f"[OTP] Valid for {Config.OTP_EXPIRY_MINUTES} minutes")
#         print("="*50 + "\n")
        
#         return True
        
#     except Exception as e:
#         print(f"[ERROR] Failed to send OTP: {e}")
#         return False

"""
OTP generation and verification module.
Handles OTP creation, hashing, and validation for both phone numbers and emails.
"""

import random
import bcrypt
from datetime import datetime
from config import Config
import db
import smtplib
from email.message import EmailMessage

# -----------------------------
# OTP Generation & Hashing
# -----------------------------

def generate_otp() -> str:
    """
    Generate a random 6-digit OTP.
    Returns:
        str: 6-digit OTP as string
    """
    return str(random.randint(100000, 999999))


def hash_otp(otp: str) -> str:
    """
    Hash an OTP using bcrypt.
    Args:
        otp (str): Plain text OTP
    Returns:
        str: Hashed OTP
    """
    return bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)).decode('utf-8')


# -----------------------------
# OTP Verification
# -----------------------------

def verify_otp(identifier: str, otp: str) -> bool:
    """
    Verify OTP against stored hash.
    Args:
        identifier (str): Phone number or email
        otp (str): OTP entered by user
    Returns:
        bool: True if valid, False otherwise
    """
    stored_hash = db.get_otp(identifier)
    if not stored_hash:
        print(f"[ERROR] No valid OTP found for {identifier}")
        return False

    try:
        is_valid = bcrypt.checkpw(otp.encode('utf-8'), stored_hash.encode('utf-8'))
        if is_valid:
            print(f"[SUCCESS] OTP verified for {identifier}")
            db.delete_otp(identifier)
        else:
            print(f"[ERROR] Invalid OTP for {identifier}")
        return is_valid
    except Exception as e:
        print(f"[ERROR] OTP verification error: {e}")
        return False


# -----------------------------
# Send OTP Functions
# -----------------------------

def send_email_otp(email: str, otp: str) -> bool:
    """
    Send OTP to user's email using Gmail SMTP. If email credentials are not
    configured or authentication fails, fall back to printing the OTP to the
    console for testing.
    """
    # If credentials are missing, fall back to printing the OTP
    if not Config.EMAIL_SENDER or not Config.EMAIL_PASSWORD:
        print(f"[WARNING] Email credentials not configured; printing OTP instead.")
        print("\n" + "="*50)
        print(f"[OTP] OTP for {email}: {otp}")
        print(f"[OTP] Valid for {Config.OTP_EXPIRY_MINUTES} minutes")
        print("="*50 + "\n")
        return True

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your OTP Code'
        msg['From'] = Config.EMAIL_SENDER
        msg['To'] = email
        msg.set_content(
            f"Your OTP for registration is: {otp}\n"
            f"Valid for {Config.OTP_EXPIRY_MINUTES} minutes."
        )

        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"[SUCCESS] OTP sent to email: {email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        # Authentication failed — print OTP and continue so testing can proceed
        print(f"[ERROR] SMTP authentication failed: {e}")
        print(f"[WARNING] Falling back to console output for OTP for {email}.")
        print("\n" + "="*50)
        print(f"[OTP] OTP for {email}: {otp}")
        print(f"[OTP] Valid for {Config.OTP_EXPIRY_MINUTES} minutes")
        print("="*50 + "\n")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send OTP email: {e}")
        # For other errors, also print OTP so user can proceed during testing
        print("\n" + "="*50)
        print(f"[OTP] OTP for {email}: {otp}")
        print(f"[OTP] Valid for {Config.OTP_EXPIRY_MINUTES} minutes")
        print("="*50 + "\n")
        return True


def send_otp(identifier: str) -> bool:
    """
    Generate and send OTP.
    Args:
        identifier (str): Phone number or email
    Returns:
        bool: True if OTP sent successfully
    """
    try:
        # Clean up expired OTPs first
        db.cleanup_expired_otps()

        # Generate and store OTP
        otp = generate_otp()
        otp_hash = hash_otp(otp)
        db.store_otp(identifier, otp_hash)

        # Send via email if identifier contains '@', else print to console
        if '@' in identifier:
            return send_email_otp(identifier, otp)
        else:
            print("\n" + "="*50)
            print(f"[OTP] OTP for {identifier}: {otp}")
            print(f"[OTP] Valid for {Config.OTP_EXPIRY_MINUTES} minutes")
            print("="*50 + "\n")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to send OTP: {e}")
        return False
