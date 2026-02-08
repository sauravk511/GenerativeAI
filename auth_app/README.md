# Secure Authentication System

A complete authentication system built with Python, Streamlit, and PostgreSQL featuring OTP verification, password hashing, and session management.

## 🎯 Features

- **User Registration** with OTP verification
- **Secure Login** with bcrypt password hashing
- **Session Management** using Streamlit session state
- **PostgreSQL Database** with proper schema design
- **OTP Expiration** (5 minutes)
- **Input Validation** and error handling
- **SQL Injection Prevention** via parameterized queries

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## 🚀 Installation

### 1. Clone or Navigate to Project Directory

```bash
cd c:\PROJECT\login_authentication\auth_app
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Ensure PostgreSQL is installed and running. Create a database:

```sql
CREATE DATABASE auth_db;
```

### 4. Configure Environment Variables

Copy the example environment file and edit it:

```bash
copy .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
OTP_EXPIRY_MINUTES=5
BCRYPT_ROUNDS=12
```

### 5. Initialize Database

The application will automatically create tables on first run. Alternatively, you can manually run:

```bash
python -c "from db import init_database; init_database()"
```

## 🏃 Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🧪 Testing

### Test Scenarios

1. **Valid Signup Flow**
   - Enter phone number (e.g., +1234567890)
   - Click "Send OTP"
   - Check console/terminal for OTP
   - Enter OTP and create password
   - Verify account created

2. **OTP Expiration**
   - Request OTP
   - Wait 5+ minutes
   - Try to verify - should fail

3. **Duplicate Account Prevention**
   - Try registering with existing phone
   - Should show error message

4. **Successful Login**
   - Enter registered phone and password
   - Should redirect to dashboard

5. **Failed Login**
   - Enter wrong password
   - Should show error message

6. **Session Persistence**
   - Login successfully
   - Refresh browser
   - Should remain logged in

7. **Logout**
   - Click logout from dashboard
   - Should redirect to login
   - Cannot access dashboard without login

## 📁 Project Structure

```
auth_app/
├── app.py              # Streamlit frontend application
├── auth.py             # Authentication logic (registration, login, session)
├── db.py               # Database operations and connection pooling
├── otp.py              # OTP generation, hashing, and verification
├── config.py           # Configuration management
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🔒 Security Features

- **bcrypt Password Hashing**: Passwords are hashed with 12 rounds
- **OTP Hashing**: OTPs are hashed before storage
- **OTP Expiration**: OTPs expire after 5 minutes
- **Parameterized Queries**: Prevents SQL injection
- **Input Validation**: Phone and password validation
- **Session Management**: Secure session state handling

## ⚠️ Known Limitations

1. **Console OTP Delivery**: OTPs are printed to console instead of SMS (testing mode)
2. **Single Server**: Not designed for distributed deployment
3. **Basic Phone Validation**: Simple regex validation (not international format aware)
4. **No Rate Limiting**: No protection against OTP spam
5. **No Account Recovery**: No password reset functionality
6. **No Multi-Factor Auth**: Only password-based after OTP verification

## 🚀 Upgrade Path to Production

### SMS Integration

Replace console OTP printing with real SMS:

1. **Choose SMS Provider**:
   - Twilio
   - AWS SNS
   - Vonage (Nexmo)
   - MessageBird

2. **Update `otp.py`**:
   ```python
   # Replace print statement with SMS API call
   from twilio.rest import Client
   
   def send_otp(phone: str):
       otp = generate_otp()
       otp_hash = hash_otp(otp)
       db.store_otp(phone, otp_hash)
       
       # Send via Twilio
       client = Client(account_sid, auth_token)
       message = client.messages.create(
           body=f"Your OTP is: {otp}",
           from_=twilio_phone,
           to=phone
       )
       return True
   ```

### Additional Production Enhancements

- Add rate limiting (e.g., Redis-based)
- Implement password reset flow
- Add email verification
- Enable 2FA/MFA
- Add logging and monitoring
- Implement HTTPS/SSL
- Add CAPTCHA for registration
- Database connection pooling optimization
- Add user profile management
- Implement account deletion

## 🛠️ Troubleshooting

### Database Connection Error

```
❌ Failed to create connection pool
```

**Solution**: Check PostgreSQL is running and `.env` credentials are correct.

### Module Import Error

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution**: Install dependencies: `pip install -r requirements.txt`

### OTP Not Showing

**Solution**: Check the terminal/console where you ran `streamlit run app.py`. OTP is printed there.

### Tables Not Created

**Solution**: Run database initialization manually:
```bash
python -c "from db import init_database; init_database()"
```

## 📝 License

This is a learning prototype. Use at your own risk.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and enhance!

---

**Built with ❤️ for learning secure authentication practices**
