"""
Database connection and operations module.
Handles PostgreSQL connections and provides data access functions.
"""

import psycopg2
from psycopg2 import pool, sql
from datetime import datetime, timedelta
from config import Config
import os


class Database:
    """Database connection and operations manager."""
    
    _connection_pool = None
    
    @classmethod
    def get_pool(cls):
        """Get or create connection pool."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.SimpleConnectionPool(
                    1,  # min connections
                    10,  # max connections
                    Config.get_db_connection_string()
                )
                print("[SUCCESS] Database connection pool created successfully")
            except Exception as e:
                print(f"[ERROR] Failed to create connection pool: {e}")
                raise
        return cls._connection_pool
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        return cls.get_pool().getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool."""
        cls.get_pool().putconn(conn)
    
    @classmethod
    def close_all_connections(cls):
        """Close all connections in the pool."""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            cls._connection_pool = None


def init_database():
    """Initialize database by creating tables from schema.sql."""
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        
        print("[SUCCESS] Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            Database.return_connection(conn)


def store_otp(phone: str, otp_hash: str, expiry_minutes: int = None):
    """
    Store OTP hash for a phone number with expiration.
    
    Args:
        phone: Phone number
        otp_hash: Hashed OTP
        expiry_minutes: Minutes until expiration (default from config)
    """
    if expiry_minutes is None:
        expiry_minutes = Config.OTP_EXPIRY_MINUTES
    
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Delete any existing OTPs for this phone
        cursor.execute("DELETE FROM otps WHERE phone = %s", (phone,))
        
        # Insert new OTP with expiration
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        cursor.execute(
            "INSERT INTO otps (phone, otp_hash, expires_at) VALUES (%s, %s, %s)",
            (phone, otp_hash, expires_at)
        )
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to store OTP: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            Database.return_connection(conn)


def get_otp(phone: str):
    """
    Retrieve OTP hash for a phone number if not expired.
    
    Args:
        phone: Phone number
        
    Returns:
        OTP hash if valid and not expired, None otherwise
    """
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Get OTP that hasn't expired
        cursor.execute(
            "SELECT otp_hash FROM otps WHERE phone = %s AND expires_at > %s",
            (phone, datetime.now())
        )
        
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else None
        
    except Exception as e:
        print(f"[ERROR] Failed to retrieve OTP: {e}")
        return None
    finally:
        if conn:
            Database.return_connection(conn)


def delete_otp(phone: str):
    """Delete OTP for a phone number after successful verification."""
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM otps WHERE phone = %s", (phone,))
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to delete OTP: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            Database.return_connection(conn)


def cleanup_expired_otps():
    """Remove all expired OTPs from database."""
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM otps WHERE expires_at < %s", (datetime.now(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        
        if deleted_count > 0:
            print(f"[CLEANUP] Cleaned up {deleted_count} expired OTP(s)")
        
        return deleted_count
        
    except Exception as e:
        print(f"[ERROR] Failed to cleanup OTPs: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            Database.return_connection(conn)


def user_exists(phone: str):
    """Check if a user with the given phone number exists."""
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        result = cursor.fetchone()
        cursor.close()
        
        return result is not None
        
    except Exception as e:
        print(f"[ERROR] Failed to check user existence: {e}")
        return False
    finally:
        if conn:
            Database.return_connection(conn)


def create_user(phone: str, password_hash: str):
    """
    Create a new verified user.
    
    Args:
        phone: Phone number
        password_hash: Hashed password
        
    Returns:
        User ID if successful, None otherwise
    """
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (phone, password_hash, verified) VALUES (%s, %s, %s) RETURNING id",
            (phone, password_hash, True)
        )
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        print(f"[SUCCESS] User created successfully: {phone}")
        return user_id
        
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            Database.return_connection(conn)


def get_user_by_phone(phone: str):
    """
    Retrieve user information by phone number.
    
    Args:
        phone: Phone number
        
    Returns:
        Dictionary with user data or None
    """
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, phone, password_hash, verified, created_at FROM users WHERE phone = %s",
            (phone,)
        )
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'id': result[0],
                'phone': result[1],
                'password_hash': result[2],
                'verified': result[3],
                'created_at': result[4]
            }
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to retrieve user: {e}")
        return None
    finally:
        if conn:
            Database.return_connection(conn)
