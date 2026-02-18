const API_URL = 'http://localhost:8000';
const username = localStorage.getItem('username');

if (!username) {
    window.location.href = 'index.html';
}

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

// Initialize
document.getElementById('username').textContent = username;
loadProfile();
loadDocuments();
loadHistory();

// Top K slider
document.getElementById('topK').addEventListener('input', (e) => {
    document.getElementById('topKValue').textContent = e.target.value;
});

// Document filter change
document.getElementById('docFilter').addEventListener('change', (e) => {
    const selectionArea = document.getElementById('docSelectionArea');
    if (e.target.value === 'selected') {
        selectionArea.style.display = 'block';
        populateDocumentCheckboxes();
    } else {
        selectionArea.style.display = 'none';
    }
});

// Populate document checkboxes
async function populateDocumentCheckboxes() {
    try {
        const res = await fetch(`${API_URL}/documents/${username}`);
        const data = await res.json();
        const area = document.getElementById('docSelectionArea');
        
        if (!data.documents || !data.documents.length) {
            area.innerHTML = '<p style="color:var(--text-muted);font-size:13px">No documents uploaded yet</p>';
            return;
        }
        
        area.innerHTML = data.documents.map(doc => `
            <label style="display:block;margin:5px 0;cursor:pointer">
                <input type="checkbox" class="doc-checkbox" value="${doc}" checked style="margin-right:8px">
                <span style="font-size:14px">${doc}</span>
            </label>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

// Section switching
function showSection(section) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(section + 'Section').classList.add('active');
    
    if (section === 'documents') loadDocuments();
    if (section === 'history') loadHistory();
    if (section === 'profile') loadProfile();
}

function logout() {
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Upload files
async function uploadFiles() {
    const files = document.getElementById('pdfFiles').files;
    const msg = document.getElementById('uploadMessage');
    
    if (!files.length) {
        msg.className = 'message error';
        msg.textContent = 'Please select files';
        return;
    }
    
    msg.className = 'message';
    msg.textContent = 'Uploading...';
    msg.style.display = 'block';
    
    let success = 0;
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);
        
        try {
            const res = await fetch(`${API_URL}/rag/upload`, {
                method: 'POST',
                body: formData
            });
            if (res.ok) success++;
        } catch (err) {
            console.error(err);
        }
    }
    
    msg.className = success ? 'message success' : 'message error';
    msg.textContent = success ? `Uploaded ${success} file(s)` : 'Upload failed';
    loadDocuments();
}

// Ask question
async function askQuestion() {
    const question = document.getElementById('question').value.trim();
    const topK = parseInt(document.getElementById('topK').value);
    const docFilter = document.getElementById('docFilter').value;
    const answerBox = document.getElementById('answerBox');
    const sourcesBox = document.getElementById('sourcesBox');
    
    if (!question) return;
    
    // Get selected documents if filter is 'selected'
    let selectedDocs = null;
    if (docFilter === 'selected') {
        const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
        selectedDocs = Array.from(checkboxes).map(cb => cb.value);
        
        if (!selectedDocs.length) {
            answerBox.innerHTML = '<span style="color:#ff3b30">Please select at least one document</span>';
            answerBox.classList.add('show');
            return;
        }
    }
    
    answerBox.innerHTML = '<em>Thinking...</em>';
    answerBox.classList.add('show');
    sourcesBox.classList.remove('show');
    
    try {
        const payload = {
            question,
            top_k: topK,
            username,
            selected_documents: selectedDocs
        };
        
        const res = await fetch(`${API_URL}/rag/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if (data.answer) {
            // Format answer with basic markdown-style rendering
            let formatted = data.answer
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
                .replace(/\n\n/g, '</p><p>')  // Paragraphs
                .replace(/\n- /g, '<br>• ')  // Bullet points
                .replace(/\n/g, '<br>');  // Line breaks
            
            answerBox.innerHTML = '<p>' + formatted + '</p>';
            
            if (data.sources && data.sources.length) {
                sourcesBox.innerHTML = '<strong>Sources:</strong><br>' + 
                    data.sources.map(s => `• ${s}`).join('<br>');
                sourcesBox.classList.add('show');
            }
        } else {
            answerBox.innerHTML = '<em>No answer returned</em>';
        }
    } catch (err) {
        answerBox.innerHTML = '<span style="color:#ff3b30">Error: ' + err.message + '</span>';
    }
}

// Load documents
async function loadDocuments() {
    try {
        const res = await fetch(`${API_URL}/documents/${username}`);
        const data = await res.json();
        const list = document.getElementById('documentsList');
        
        if (!data.documents || !data.documents.length) {
            list.innerHTML = '<p style="color: var(--text-muted)">No documents uploaded yet</p>';
            return;
        }
        
        list.innerHTML = data.documents.map(doc => `
            <div class="doc-item">
                <span>📄 ${doc}</span>
                <button onclick="deleteDocument('${doc}')">Delete</button>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

// Delete document
async function deleteDocument(doc) {
    if (!confirm('Delete this document?')) return;
    
    try {
        await fetch(`${API_URL}/documents/${username}/${doc}`, { method: 'DELETE' });
        loadDocuments();
    } catch (err) {
        console.error(err);
    }
}

// Load history
async function loadHistory() {
    try {
        const res = await fetch(`${API_URL}/history/${username}`);
        const data = await res.json();
        const list = document.getElementById('historyList');
        
        if (!data.history || !data.history.length) {
            list.innerHTML = '<p style="color: var(--text-muted)">No conversations yet</p>';
            return;
        }
        
        list.innerHTML = data.history.slice(-20).reverse().map((chat, i) => `
            <div class="history-item" onclick="this.classList.toggle('expanded')">
                <div class="history-question">${chat.question.substring(0, 60)}...</div>
                <div class="history-answer"><strong>Answer:</strong> ${chat.answer}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

// Load profile
async function loadProfile() {
    try {
        const res = await fetch(`${API_URL}/profile/${username}`);
        const data = await res.json();
        
        document.getElementById('profileUsername').textContent = data.username;
        document.getElementById('profileEmail').textContent = data.email;
        document.getElementById('profileCreated').textContent = data.created_at?.substring(0, 10) || '';
        
        document.getElementById('newUsername').value = data.username;
        document.getElementById('newEmail').value = data.email;
    } catch (err) {
        console.error(err);
    }
}

// Update profile
document.getElementById('updateProfileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const newUsername = document.getElementById('newUsername').value;
    const newEmail = document.getElementById('newEmail').value;
    const msg = document.getElementById('profileMessage');
    
    try {
        const res = await fetch(`${API_URL}/profile/${username}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_username: newUsername, new_email: newEmail })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Profile updated! Email notification sent.';
            if (data.username !== username) {
                localStorage.setItem('username', data.username);
                setTimeout(() => location.reload(), 1500);
            }
        } else {
            msg.className = 'message error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Error: ' + err.message;
    }
});

// Change password
document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const newPassword2 = document.getElementById('newPassword2').value;
    const msg = document.getElementById('passwordMessage');
    
    if (newPassword !== newPassword2) {
        msg.className = 'message error';
        msg.textContent = 'Passwords don\'t match';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/auth/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, old_password: oldPassword, new_password: newPassword })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Password changed! Email notification sent.';
            e.target.reset();
        } else {
            msg.className = 'message error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Error: ' + err.message;
    }
});
