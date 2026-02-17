# Complete Setup Guide - HTML Frontend + Email Notifications

## 🎉 What's New

### 1. **HTML/CSS Frontend**
- Clean, modern interface with HTML/CSS/JavaScript
- No Streamlit dependency for frontend
- Runs on separate port (3000)
- Full feature parity with Streamlit version

### 2. **Enhanced Email Notifications**
- Professional HTML email templates
- Automated emails for:
  - ✅ Account registration (welcome email)
  - ✅ Password change (security notification)
  - ✅ Password reset request (with secure link)
  - ✅ Password reset completion (confirmation)
  - ✅ Profile update (security notification)

### 3. **Dual Frontend Support**
- **HTML Frontend**: `http://localhost:3000` (new)
- **Streamlit Frontend**: `http://localhost:8501` (existing, still works)
- Both use the same backend API
- Choose whichever you prefer!

## 📁 New File Structure

```
RAG/
├── frontend/                    # ✨ NEW - HTML Frontend
│   ├── index.html              # Login/Signup page
│   ├── dashboard.html          # Main dashboard
│   ├── reset-password.html     # Password reset page
│   ├── css/
│   │   └── style.css           # Complete styling
│   └── js/
│       ├── auth.js             # Authentication logic
│       ├── dashboard.js        # Dashboard logic
│       └── reset.js            # Password reset logic
│
├── serve_frontend.py           # ✨ NEW - Frontend server
├── email_service.py            # ✏️ ENHANCED - Professional templates
├── main.py                     # ✏️ ENHANCED - API endpoints for frontend
├── auth.py                     # ✏️ ENHANCED - Email triggers
│
└── streamlit_app.py            # ✅ UNCHANGED - Still works!
```

## 🚀 Installation & Setup

### 1. Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
# or
uv sync
```

### 2. Configure Email (Optional but Recommended)

Edit `.env` file:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the app password (not your regular password)

**Note:** App works without email config, but notifications won't be sent.

### 3. Start the Application

You need **2 terminals**:

**Terminal 1 - Backend:**
```bash
uvicorn main:app --reload
```
✅ Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend (Choose ONE):**

**Option A - HTML Frontend (NEW):**
```bash
python3 serve_frontend.py
```
✅ Frontend runs on `http://localhost:3000`

**Option B - Streamlit Frontend (EXISTING):**
```bash
streamlit run streamlit_app.py
```
✅ Frontend runs on `http://localhost:8501`

## 🌐 Access the Application

### HTML Frontend (Recommended)
- **URL:** http://localhost:3000
- **Login:** http://localhost:3000/index.html
- **Dashboard:** http://localhost:3000/dashboard.html

### Streamlit Frontend (Alternative)
- **URL:** http://localhost:8501

## ✨ Features

### HTML Frontend Features
- ✅ Clean, modern UI with neon green theme
- ✅ Light/Dark mode toggle (persists in browser)
- ✅ Login/Signup/Forgot Password
- ✅ PDF upload and processing
- ✅ AI-powered chat with documents
- ✅ Document management
- ✅ Chat history
- ✅ User profile management
- ✅ Password change
- ✅ Responsive design

### Email Notifications
All emails are professionally designed with:
- ✅ HTML formatting
- ✅ Branded colors (neon green)
- ✅ Security notices
- ✅ Clear call-to-action buttons
- ✅ Mobile-friendly design

## 📧 Email Triggers

| Action | Email Sent | Content |
|--------|-----------|---------|
| Sign Up | Welcome Email | Account confirmation + getting started |
| Forgot Password | Reset Link | Secure token link (1-hour expiry) |
| Password Reset Complete | Confirmation | Success notification + security notice |
| Change Password | Security Alert | Password changed notification |
| Update Profile | Security Alert | Profile updated notification |

## 🎨 Theme System

### Dark Mode (Default)
- Neon green (#00ff88) accents
- Dark gradient background
- Glass-morphism cards

### Light Mode
- Blue (#3b82f6) accents
- Light gradient background
- Clean white cards

**Toggle:** Click 🌓/☀️ icon in top-right corner

## 🔒 Security Features

1. **Password Security:**
   - SHA-256 hashing
   - Minimum 6 characters
   - Confirmation required

2. **Reset Tokens:**
   - Cryptographically secure (32 bytes)
   - 1-hour expiration
   - Single-use only

3. **Email Validation:**
   - Format checking
   - Uniqueness validation
   - Security notifications

4. **CORS Protection:**
   - Only localhost:3000 allowed
   - Credentials required

## 📊 API Endpoints (for reference)

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `POST /auth/forgot-password` - Request reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/change-password` - Change password

### Profile
- `GET /profile/{username}` - Get profile
- `PUT /profile/{username}` - Update profile

### Documents
- `POST /rag/upload` - Upload PDF
- `GET /documents/{username}` - List documents
- `DELETE /documents/{username}/{doc}` - Delete document

### Chat
- `POST /rag/query` - Ask question
- `GET /history/{username}` - Get chat history

## 🔄 Migration from Streamlit

If you prefer HTML frontend:

1. **No migration needed!** Both frontends work simultaneously
2. All user data is shared (same backend)
3. Switch between frontends anytime
4. Existing users can login to HTML frontend immediately

## 🧪 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can create new account
- [ ] Welcome email received (if configured)
- [ ] Can login with new account
- [ ] Can upload PDF files
- [ ] Can ask questions and get answers
- [ ] Can view documents
- [ ] Can delete documents
- [ ] Can view chat history
- [ ] Can update profile
- [ ] Profile update email received
- [ ] Can change password
- [ ] Password change email received
- [ ] Can request password reset
- [ ] Reset email received with link
- [ ] Can reset password via link
- [ ] Reset confirmation email received
- [ ] Theme toggle works
- [ ] Theme persists on refresh

## 🐛 Troubleshooting

### Frontend won't load
```bash
# Check if port 3000 is available
lsof -i :3000

# Try different port
python3 -m http.server 3001 --directory frontend
```

### Backend errors
```bash
# Check if port 8000 is available
lsof -i :8000

# Check logs
tail -f backend.log
```

### Email not sending
- Verify SMTP credentials in .env
- For Gmail, use App Password (not regular password)
- Check console for error messages
- App works without email (just no notifications)

### CORS errors
- Ensure backend is running
- Check browser console for details
- Verify frontend URL matches CORS config

## 📝 Email Template Customization

Edit `email_service.py` to customize:
- Email subject lines
- HTML templates
- Colors and branding
- Button text
- Footer content

## 🎯 Key Differences: HTML vs Streamlit

| Feature | HTML Frontend | Streamlit Frontend |
|---------|--------------|-------------------|
| Port | 3000 | 8501 |
| Technology | HTML/CSS/JS | Python/Streamlit |
| Theme Toggle | ✅ Persists | ✅ Session only |
| Performance | Faster | Slightly slower |
| Customization | Full control | Limited |
| Deployment | Static files | Python server |

## 🚀 Production Deployment

### HTML Frontend
```bash
# Serve with nginx, Apache, or any static host
# Just copy frontend/ folder to web server
```

### Backend
```bash
# Use gunicorn or similar
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📞 Support

- Check console logs for errors
- Verify .env configuration
- Ensure all dependencies installed
- Test with curl/Postman for API issues

## 🎉 Success!

You now have:
- ✅ Modern HTML/CSS frontend
- ✅ Professional email notifications
- ✅ Dual frontend support (HTML + Streamlit)
- ✅ Complete RAG chat system
- ✅ User authentication & profiles
- ✅ Theme switching
- ✅ Production-ready architecture

**Enjoy your enhanced RAG PDF Chat application!** 🚀
