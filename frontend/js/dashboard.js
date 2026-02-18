const API_URL = 'http://localhost:8000';
const username = localStorage.getItem('username');
const token = localStorage.getItem('token');

if (!username || !token) {
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
        const res = await fetch(`${API_URL}/documents`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const area = document.getElementById('docSelectionArea');
        
        if (!data.data || !data.data.documents || !data.data.documents.length) {
            area.innerHTML = '<p style="color:var(--text-muted);font-size:13px">No documents uploaded yet</p>';
            return;
        }
        
        area.innerHTML = data.data.documents.map(doc => `
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
    localStorage.removeItem('token');
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
        
        try {
            const res = await fetch(`${API_URL}/rag/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await res.json();
            if (data.success) success++;
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
            selected_documents: selectedDocs
        };
        
        const res = await fetch(`${API_URL}/rag/query`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if (data.success && data.data && data.data.answer) {
            // Format answer with basic markdown-style rendering
            let formatted = data.data.answer
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
                .replace(/\n\n/g, '</p><p>')  // Paragraphs
                .replace(/\n- /g, '<br>• ')  // Bullet points
                .replace(/\n/g, '<br>');  // Line breaks
            
            answerBox.innerHTML = '<p>' + formatted + '</p>';
            
            if (data.data.sources && data.data.sources.length) {
                sourcesBox.innerHTML = '<strong>Sources:</strong><br>' + 
                    data.data.sources.map(s => `• ${s}`).join('<br>');
                sourcesBox.classList.add('show');
            }
        } else {
            answerBox.innerHTML = '<em>' + (data.message || 'No answer returned') + '</em>';
        }
    } catch (err) {
        answerBox.innerHTML = '<span style="color:#ff3b30">Error: ' + err.message + '</span>';
    }
}

// Load documents
async function loadDocuments() {
    try {
        const res = await fetch(`${API_URL}/documents`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const list = document.getElementById('documentsList');
        
        if (!data.data || !data.data.documents || !data.data.documents.length) {
            list.innerHTML = '<p style="color: var(--text-muted)">No documents uploaded yet</p>';
            return;
        }
        
        list.innerHTML = data.data.documents.map(doc => `
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
        await fetch(`${API_URL}/documents/${doc}`, { 
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        loadDocuments();
    } catch (err) {
        console.error(err);
    }
}

// Load history
async function loadHistory() {
    try {
        const res = await fetch(`${API_URL}/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const list = document.getElementById('historyList');
        
        if (!data.data || !data.data.history || !data.data.history.length) {
            list.innerHTML = '<p style="color: var(--text-muted)">No conversations yet</p>';
            return;
        }
        
        list.innerHTML = data.data.history.slice(-20).reverse().map((chat, i) => `
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
        const res = await fetch(`${API_URL}/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        if (data.success && data.data) {
            document.getElementById('profileUsername').textContent = data.data.username;
            document.getElementById('profileEmail').textContent = data.data.email;
            document.getElementById('profileCreated').textContent = data.data.created_at?.substring(0, 10) || '';
            
            document.getElementById('newUsername').value = data.data.username;
            document.getElementById('newEmail').value = data.data.email;
        }
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
        const res = await fetch(`${API_URL}/profile`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ new_username: newUsername, new_email: newEmail })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Profile updated!';
            if (data.data && data.data.username !== username) {
                localStorage.setItem('username', data.data.username);
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
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'Password changed!';
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


// ========== DATA ANALYSIS FUNCTIONS ==========

let currentDataFile = null;

// Upload data file
async function uploadDataFile() {
    const fileInput = document.getElementById('dataFile');
    const msg = document.getElementById('dataUploadMessage');
    
    if (!fileInput.files.length) {
        msg.className = 'message error';
        msg.textContent = 'Please select a file';
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    msg.className = 'message';
    msg.textContent = 'Uploading and analyzing...';
    
    try {
        const res = await fetch(`${API_URL}/data/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        
        const data = await res.json();
        
        if (data.success) {
            msg.className = 'message success';
            msg.textContent = 'File analyzed successfully!';
            currentDataFile = data.data.filename;
            
            // Show preview
            displayDataPreview(data.data.preview);
            
            // Load insights and charts
            loadDataInsights(currentDataFile);
            loadDataCharts(currentDataFile);
            
            // Show query section
            document.getElementById('dataQuery').style.display = 'block';
        } else {
            msg.className = 'message error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'message error';
        msg.textContent = 'Upload failed: ' + err.message;
    }
}

// Display data preview
function displayDataPreview(preview) {
    const previewDiv = document.getElementById('dataPreview');
    const tableDiv = document.getElementById('previewTable');
    
    if (!preview || preview.length === 0) return;
    
    // Create table
    let html = '<table style="width:100%; border-collapse:collapse;">';
    
    // Header
    html += '<thead><tr>';
    Object.keys(preview[0]).forEach(key => {
        html += `<th style="border:1px solid #ddd; padding:8px; background:#f5f5f5;">${key}</th>`;
    });
    html += '</tr></thead>';
    
    // Rows
    html += '<tbody>';
    preview.forEach(row => {
        html += '<tr>';
        Object.values(row).forEach(val => {
            html += `<td style="border:1px solid #ddd; padding:8px;">${val}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    tableDiv.innerHTML = html;
    previewDiv.style.display = 'block';
}

// Load insights
async function loadDataInsights(filename) {
    try {
        const res = await fetch(`${API_URL}/data/analysis/${filename}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await res.json();
        
        if (data.success) {
            const insightsDiv = document.getElementById('insightsContent');
            insightsDiv.innerHTML = `<p style="white-space:pre-wrap;">${data.data.llm_insights}</p>`;
            document.getElementById('dataInsights').style.display = 'block';
        }
    } catch (err) {
        console.error('Failed to load insights:', err);
    }
}

// Load charts
async function loadDataCharts(filename) {
    try {
        const res = await fetch(`${API_URL}/data/charts/${filename}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await res.json();
        
        if (data.success && data.data.charts.length > 0) {
            const container = document.getElementById('chartsContainer');
            container.innerHTML = '';
            
            data.data.charts.forEach((chart, idx) => {
                const chartDiv = document.createElement('div');
                chartDiv.id = `chart-${idx}`;
                chartDiv.style.marginBottom = '20px';
                container.appendChild(chartDiv);
                
                const plotlyData = JSON.parse(chart.data);
                Plotly.newPlot(chartDiv.id, plotlyData.data, plotlyData.layout);
            });
            
            document.getElementById('dataCharts').style.display = 'block';
        }
    } catch (err) {
        console.error('Failed to load charts:', err);
    }
}

// Ask question about data
async function askDataQuestion() {
    const question = document.getElementById('dataQuestion').value.trim();
    const answerDiv = document.getElementById('dataAnswer');
    
    if (!question) return;
    if (!currentDataFile) {
        answerDiv.className = 'message error';
        answerDiv.textContent = 'Please upload a file first';
        return;
    }
    
    answerDiv.className = 'message';
    answerDiv.textContent = 'Analyzing...';
    
    try {
        const res = await fetch(`${API_URL}/data/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ filename: currentDataFile, question })
        });
        
        const data = await res.json();
        
        if (data.success) {
            answerDiv.className = 'message success';
            answerDiv.textContent = data.data.answer;
        } else {
            answerDiv.className = 'message error';
            answerDiv.textContent = data.message;
        }
    } catch (err) {
        answerDiv.className = 'message error';
        answerDiv.textContent = 'Query failed: ' + err.message;
    }
}
