# 🔍 Registration Troubleshooting Guide

## Status Check
- **Backend**: Running on `http://localhost:8000` ✅
- **Frontend**: Running on `http://localhost:5173` ✅
- **Database**: SQLite (Default) ✅

## Common Issues & Fixes

### 1. "Network Error"
**Cause**: Frontend cannot connect to Backend.
**Fix**:
1. Ensure BOTH servers are running.
2. Check if `http://localhost:8000/api/` loads in your browser.
3. If not, restart backend:
   ```bash
   cd backend
   python manage.py runserver
   ```

### 2. "Registration Failed" (400 Bad Request)
**Cause**: Username already exists or passwords don't match.
**Fix**:
- Try a different username (e.g., `user_2025`)
- Ensure passwords match exactly
- Password must be at least 8 characters (Django default)

### 3. "Authentication credentials were not provided" (401 Unauthorized)
**Cause**: You are trying to access a protected page without logging in.
**Fix**:
- Go to Register page first
- Create an account
- Then Login

## 🚀 Try This Test Sequence

1. **Stop Everything**: Close all terminals.
2. **Start Backend**:
   ```bash
   cd backend
   python manage.py runserver
   ```
3. **Start Frontend**:
   ```bash
   cd web-frontend
   npm run dev
   ```
4. **Open Browser**: Go to `http://localhost:5173`
5. **Register**:
   - Username: `test_new_user`
   - Password: `TestPassword123!`
   - Confirm: `TestPassword123!`

If this fails, please check the terminal running the **Backend** for any error messages when you click "Register".
