const API_URL = 'http://localhost:8000';

// Get token from URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (!token) {
    document.getElementById('resetMessage').className = 'message error';
    document.getElementById('resetMessage').textContent = 'Invalid reset link';
}

// Reset password
document.getElementById('resetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const newPassword = document.getElementById('newPassword').value;
    const newPassword2 = document.getElementById('newPassword2').value;
    const msg = document.getElementById('resetMessage');
    
    if (newPassword !== newPassword2) {
        msg.className = 'message error';
        msg.textContent = 'Passwords don\'t match';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, new_password: newPassword })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Password reset successful! Redirecting to login...';
            setTimeout(() => window.location.href = 'index.html', 2000);
        } else {
            msg.className = 'message error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Connection error';
    }
});
