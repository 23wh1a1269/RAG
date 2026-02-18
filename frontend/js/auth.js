const API_URL = 'http://localhost:8000';

// Theme toggle
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('theme') || 'dark';
if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    themeToggle.textContent = isLight ? '☀️' : '🌓';
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
});

// Tab switching
function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form').forEach(f => f.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tab + 'Form').classList.add('active');
}

// Login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const msg = document.getElementById('loginMessage');
    
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
            msg.className = 'message success';
            msg.textContent = 'Login successful! Redirecting...';
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else {
            msg.className = 'message error';
            msg.textContent = data.message || 'Login failed';
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Connection error';
    }
});

// Signup
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const password2 = document.getElementById('signupPassword2').value;
    const msg = document.getElementById('signupMessage');
    
    if (password !== password2) {
        msg.className = 'message error';
        msg.textContent = 'Passwords don\'t match';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Account created! Redirecting to login...';
            setTimeout(() => {
                document.querySelector('.tab').click();
                document.getElementById('loginUsername').value = username;
            }, 2000);
        } else {
            msg.className = 'message error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Connection error';
    }
});
