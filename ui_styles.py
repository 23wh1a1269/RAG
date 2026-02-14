def get_custom_css():
    return """
<style>

body {
    background: #0b0f1a;
}

.center-wrapper {
    max-width: 420px;
    margin: auto;
    padding-top: 8vh;
}

.app-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: white;
}

.app-subtitle {
    text-align: center;
    color: #9aa4b2;
    margin-bottom: 30px;
}

.glass-card {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    margin-bottom: 20px;
}

.auth-width {
    width: 100%;
}

.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.welcome {
    color: #9aa4b2;
    font-size: 14px;
}

.username {
    font-size: 28px;
    font-weight: 700;
    color: white;
}

.quota-box {
    text-align: right;
}

.quota-label {
    color: #9aa4b2;
    font-size: 12px;
}

.quota-value {
    font-size: 24px;
    color: #6c8cff;
    font-weight: 700;
}

.answer-box {
    background: rgba(108,140,255,0.12);
    border-left: 4px solid #6c8cff;
    padding: 16px;
    border-radius: 10px;
    margin-top: 16px;
}

.stButton>button {
    border-radius: 10px;
    font-weight: 600;
}

</style>
"""
