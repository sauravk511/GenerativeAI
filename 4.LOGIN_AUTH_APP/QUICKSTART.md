# Quick Start Guide

## Prerequisites Check

Before running the application, ensure you have:

1. ✅ Python 3.8+ installed
2. ✅ PostgreSQL installed and running
3. ✅ Dependencies installed (`pip install -r requirements.txt`)

## Step-by-Step Setup

### 1. Install PostgreSQL (if not already installed)

Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

During installation:
- Remember the password you set for the `postgres` user
- Default port is usually 5432

### 2. Create Database

Open PostgreSQL command line (SQL Shell / psql) or pgAdmin and run:

```sql
CREATE DATABASE auth_db;
```

Or use the command line:
```bash
# If PostgreSQL is in PATH:
psql -U postgres -c "CREATE DATABASE auth_db;"

# You'll be prompted for the postgres password
```

### 3. Configure Environment

Edit the `.env` file with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
OTP_EXPIRY_MINUTES=5
BCRYPT_ROUNDS=12
```

### 4. Initialize Database

Run the setup script:

```bash
python setup_db.py
```

This will:
- Test database connection
- Create required tables (users, otps)
- Verify setup

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Testing the Application

### Test 1: User Registration

1. Click "Create Account"
2. Enter a phone number (e.g., `+1234567890`)
3. Click "Send OTP"
4. **Check the terminal/console** where you ran `streamlit run app.py`
5. You'll see output like:
   ```
   ==================================================
   📱 OTP for +1234567890: 123456
   ⏰ Valid for 5 minutes
   ==================================================
   ```
6. Enter the OTP and create a password
7. Click "Verify & Register"

### Test 2: Login

1. Enter your registered phone number
2. Enter your password
3. Click "Login"
4. You should see the dashboard

### Test 3: Session & Logout

1. After logging in, refresh the browser
2. You should still be logged in (session persistence)
3. Click "Logout"
4. You should be redirected to login page

## Troubleshooting

### "Database connection failed"

**Problem**: Cannot connect to PostgreSQL

**Solutions**:
1. Ensure PostgreSQL service is running:
   - Windows: Check Services (services.msc) for "postgresql-x64-XX"
   - Or search for "Services" in Start menu
2. Verify credentials in `.env` file
3. Check if database `auth_db` exists

### "Module not found"

**Problem**: Missing Python packages

**Solution**:
```bash
python -m pip install -r requirements.txt
```

### "OTP not showing"

**Problem**: Can't see the OTP

**Solution**: 
- OTP is printed in the **terminal/console** where you ran `streamlit run app.py`
- NOT in the browser
- Look for the section with 📱 emoji

### PostgreSQL not in PATH

**Problem**: `psql` command not found

**Solution**:
1. Find PostgreSQL installation directory (usually `C:\Program Files\PostgreSQL\XX\bin`)
2. Add to PATH, or
3. Use pgAdmin GUI tool instead
4. Or use full path: `"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres`

## Quick Test Commands

```bash
# Test database connection
python -c "from db import Database; conn = Database.get_connection(); print('✅ Connected'); Database.return_connection(conn)"

# Initialize database
python setup_db.py

# Run application
streamlit run app.py
```

## Default Test Credentials

After setup, you can create a test account:
- Phone: `+1234567890`
- Password: `test123`

(You'll need to go through OTP verification first)

## Need Help?

1. Check the main README.md for detailed documentation
2. Verify PostgreSQL is running
3. Check `.env` file configuration
4. Look at terminal output for error messages
