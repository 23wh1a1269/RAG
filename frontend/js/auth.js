const API_URL = 'http://localhost:8000';

// Tab switching
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Update tabs
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update forms
        document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
        document.getElementById(tabName + 'Form').classList.add('active');
    });
});

// Password toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const type = input.type === 'password' ? 'text' : 'password';
    input.type = type;
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Show message in form
function showMessage(elementId, message, type) {
    const msgEl = document.getElementById(elementId);
    msgEl.textContent = message;
    msgEl.className = `message ${type} show`;
    
    setTimeout(() => {
        msgEl.classList.remove('show');
    }, 5000);
}

// Login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn-primary');
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    btn.classList.add('loading');
    
    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        
        if (data.success && data.data && data.data.token) {
            localStorage.setItem('username', username);
            localStorage.setItem('token', data.data.token);
            showToast('Login successful! Redirecting...', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else {
            showMessage('loginMessage', data.message || 'Login failed', 'error');
        }
    } catch (err) {
        showMessage('loginMessage', 'Connection error. Please try again.', 'error');
    } finally {
        btn.classList.remove('loading');
    }
});

// Signup
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn-primary');
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const password2 = document.getElementById('signupPassword2').value;
    
    if (password !== password2) {
        showMessage('signupMessage', 'Passwords don\'t match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('signupMessage', 'Password must be at least 6 characters', 'error');
        return;
    }
    
    btn.classList.add('loading');
    
    try {
        const res = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('Account created successfully!', 'success');
            showMessage('signupMessage', 'Account created! Switching to login...', 'success');
            setTimeout(() => {
                document.querySelector('[data-tab="login"]').click();
                document.getElementById('loginUsername').value = username;
            }, 2000);
        } else {
            showMessage('signupMessage', data.message, 'error');
        }
    } catch (err) {
        showMessage('signupMessage', 'Connection error. Please try again.', 'error');
    } finally {
        btn.classList.remove('loading');
    }
});
