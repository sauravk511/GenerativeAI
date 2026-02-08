# """
# SQLite database adapter for testing without PostgreSQL.
# This is a drop-in replacement for db.py that uses SQLite instead.
# """

# import sqlite3
"""
SQLite database adapter for authentication system.
Supports users registered with phone or email and OTPs.
Includes robust error handling and duplicate checks.
"""

import sqlite3
from datetime import datetime, timedelta
from config import Config
import os
import threading

class Database:
    _connection = None
    _lock = threading.Lock()
    _db_path = os.path.join(os.path.dirname(__file__), 'auth_app.db')

    @classmethod
    def get_connection(cls):
        """Get or create SQLite connection (thread-safe)."""
        with cls._lock:
            if cls._connection is None:
                cls._connection = sqlite3.connect(cls._db_path, check_same_thread=False)
                cls._connection.row_factory = sqlite3.Row
                print(f"[SUCCESS] Database connection created: {cls._db_path}")
            return cls._connection

    @classmethod
    def return_connection(cls, conn):
        pass

    @classmethod
    def close_all_connections(cls):
        with cls._lock:
            if cls._connection:
                cls._connection.close()
                cls._connection = None


def init_database():
    """Create users and OTP tables if they don't exist."""
    conn = Database.get_connection()
    cursor = conn.cursor()

    try:
        # Users table supports phone OR email
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK(phone IS NOT NULL OR email IS NOT NULL)
            )
        """)

        # OTP table supports phone OR email as identifier
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                identifier TEXT NOT NULL,
                otp_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_otps_identifier ON otps(identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_otps_expires ON otps(expires_at)")

        conn.commit()
        print("[SUCCESS] Database tables created successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise


# -------------------- OTP FUNCTIONS --------------------
def store_otp(identifier: str, otp_hash: str, expiry_minutes: int = None):
    """Store OTP hash for phone/email with expiration."""
    if expiry_minutes is None:
        expiry_minutes = Config.OTP_EXPIRY_MINUTES
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # Remove existing OTP
        cursor.execute("DELETE FROM otps WHERE identifier = ?", (identifier,))
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)

        cursor.execute(
            "INSERT INTO otps (identifier, otp_hash, expires_at) VALUES (?, ?, ?)",
            (identifier, otp_hash, expires_at.isoformat())
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to store OTP: {e}")
        if conn:
            conn.rollback()
        return False


def get_otp(identifier: str):
    """Retrieve OTP hash for phone/email if not expired."""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT otp_hash FROM otps WHERE identifier = ? AND expires_at > ?",
            (identifier, datetime.now().isoformat())
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve OTP: {e}")
        return None


def delete_otp(identifier: str):
    """Delete OTP after successful verification."""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otps WHERE identifier = ?", (identifier,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete OTP: {e}")
        if conn:
            conn.rollback()
        return False


def cleanup_expired_otps():
    """Remove expired OTPs from DB."""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otps WHERE expires_at < ?", (datetime.now().isoformat(),))
        deleted_count = cursor.rowcount
        conn.commit()
        if deleted_count > 0:
            print(f"[CLEANUP] Cleaned up {deleted_count} expired OTP(s)")
        return deleted_count
    except Exception as e:
        print(f"[ERROR] Failed to cleanup OTPs: {e}")
        if conn:
            conn.rollback()
        return 0


# -------------------- USER FUNCTIONS --------------------
def user_exists(identifier: str):
    """Check if user exists by phone or email."""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        if '@' in identifier:
            cursor.execute("SELECT id FROM users WHERE email = ?", (identifier,))
        else:
            cursor.execute("SELECT id FROM users WHERE phone = ?", (identifier,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"[ERROR] Failed to check user existence: {e}")
        return False


def create_user(identifier: str, password_hash: str):
    """Create a new verified user if not already exists."""
    if user_exists(identifier):
        print(f"[ERROR] User already exists: {identifier}")
        return None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        if '@' in identifier:
            cursor.execute(
                "INSERT INTO users (email, password_hash, verified) VALUES (?, ?, ?)",
                (identifier, password_hash, 1)
            )
        else:
            cursor.execute(
                "INSERT INTO users (phone, password_hash, verified) VALUES (?, ?, ?)",
                (identifier, password_hash, 1)
            )
        user_id = cursor.lastrowid
        conn.commit()
        print(f"[SUCCESS] User created successfully: {identifier}")
        return user_id
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        if conn:
            conn.rollback()
        return None


def get_user_by_identifier(identifier: str):
    """Retrieve user by phone or email."""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        if '@' in identifier:
            cursor.execute(
                "SELECT id, phone, email, password_hash, verified, created_at FROM users WHERE email = ?",
                (identifier,)
            )
        else:
            cursor.execute(
                "SELECT id, phone, email, password_hash, verified, created_at FROM users WHERE phone = ?",
                (identifier,)
            )
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'phone': result[1],
                'email': result[2],
                'password_hash': result[3],
                'verified': bool(result[4]),
                'created_at': datetime.fromisoformat(result[5]) if result[5] else datetime.now()
            }
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve user: {e}")
        return None
