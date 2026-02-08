# """
# Configuration management for the authentication system.
# Loads and validates environment variables.
# """

# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()


# class Config:
#     """Application configuration class."""
    
#     # Database Configuration
#     # DB_HOST = os.getenv('DB_HOST', 'localhost')
#     # DB_PORT = int(os.getenv('DB_PORT', '5432'))
#     # DB_NAME = os.getenv('DB_NAME', 'auth_db')
#     # DB_USER = os.getenv('DB_USER', 'postgres')
#     # DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
#     # Security Settings
#     OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', '5'))
#     BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
    
#     @classmethod
#     def validate(cls):
#         """Validate that all required configuration is present."""
#         required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
#         missing = []
        
#         for var in required_vars:
#             if not getattr(cls, var):
#                 missing.append(var)
        
#         if missing:
#             raise ValueError(
#                 f"Missing required configuration: {', '.join(missing)}. "
#                 "Please create a .env file based on .env.example"
#             )
        
#         return True
    
#     @classmethod
#     def get_db_connection_string(cls):
#         """Get PostgreSQL connection string."""
#         return (
#             f"host={cls.DB_HOST} "
#             f"port={cls.DB_PORT} "
#             f"dbname={cls.DB_NAME} "
#             f"user={cls.DB_USER} "
#             f"password={cls.DB_PASSWORD}"
#         )


# # Validate configuration on import
# try:
#     Config.validate()
# except ValueError as e:
#     print(f"⚠️  Configuration Warning: {e}")

# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env in parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)


class Config:
    # -----------------------------
    # Security Settings
    # -----------------------------
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))

    # -----------------------------
    # Email Settings (for Gmail OTP)
    # -----------------------------
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")  # e.g., your_email@gmail.com
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # app password
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    # -----------------------------
    # SQLite Database
    # -----------------------------
    DB_PATH = os.path.join(os.path.dirname(__file__), "auth_app.db")
