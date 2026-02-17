# Enhanced RAG PDF Chat - Setup Guide

## New Features Added

### 1. **Complete Authentication System**
- Email-based signup with validation
- Secure login with hashed passwords
- Forgot password functionality with token-based reset
- Email notifications on registration and password reset

### 2. **User Profile Management**
- View profile information (username, email, join date, quotas)
- Update username and email
- Change password securely
- Profile displayed in dedicated tab

### 3. **Theme Switching**
- **Dark Mode**: Neon green + black aesthetic (default)
- **Light Mode**: Clean, soft complementary palette
- Toggle button in top-left corner
- Theme persists during session

### 4. **Modern UI/UX**
- Clean, minimal design with proper spacing
- Neon green accent color in dark mode
- Smooth transitions and visual hierarchy
- Glass-morphism cards with backdrop blur
- Responsive layout

## Installation

1. **Install new dependencies:**
```bash
pip install -r requirements.txt
# or
uv sync
```

2. **Configure email (optional but recommended):**

Edit `.env` file:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**For Gmail:**
- Enable 2-factor authentication
- Generate an App Password: https://myaccount.google.com/apppasswords
- Use the app password in SMTP_PASSWORD

3. **Start the application:**
```bash
# Terminal 1: Backend
uvicorn main:app --reload

# Terminal 2: Frontend
streamlit run streamlit_app.py
```

## New Files

- `email_service.py` - Email sending functionality
- `theme.py` - Light/dark theme CSS
- Enhanced `auth.py` - Profile and password reset
- Enhanced `streamlit_app.py` - Complete UI with new features

## Usage

### Sign Up
1. Click "Create Account" tab
2. Enter username, email, and password
3. Receive welcome email (if configured)

### Forgot Password
1. Click "Forgot Password" tab
2. Enter your email
3. Check email for reset link
4. Click link and set new password

### Profile Management
1. Login and go to "Profile" tab
2. Update username/email
3. Change password securely

### Theme Switching
- Click 🌓 (moon) icon in top-left to toggle dark mode
- Click ☀️ (sun) icon to toggle light mode

## Email Configuration Notes

- Email is **optional** - app works without it
- Without email config, password reset won't send emails
- Welcome emails won't be sent but signup still works
- Console will show "Email not configured" message

## Security Features

- SHA-256 password hashing
- Secure token-based password reset (1-hour expiry)
- Email validation
- Username uniqueness check
- Session-based authentication

## Backward Compatibility

✅ All existing features preserved:
- PDF upload and RAG workflow
- Chat functionality
- Document management
- Chat history
- User quotas
- Backend API unchanged

## Theme Colors

**Dark Mode (Default):**
- Primary: Neon Green (#00ff88)
- Background: Dark gradient (#0a0e1a → #1a1f2e)
- Cards: Semi-transparent green tint

**Light Mode:**
- Primary: Blue (#3b82f6)
- Background: Light gradient (#f5f7fa → #e8ecf1)
- Cards: White with subtle shadows

## Troubleshooting

**Email not sending:**
- Check SMTP credentials in .env
- For Gmail, use App Password not regular password
- Verify 2FA is enabled on Gmail account

**Theme not switching:**
- Clear browser cache
- Refresh page after toggle

**Profile update issues:**
- Username must be unique
- Email must be valid format
- Password must be 6+ characters

## Future Enhancements

- OAuth integration (Google, GitHub)
- Two-factor authentication
- Email verification on signup
- Profile picture upload
- Custom theme colors
