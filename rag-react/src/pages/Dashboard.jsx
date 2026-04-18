import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import BentoCard from '../components/BentoCard';
import Button from '../components/Button';
import Input from '../components/Input';
import { profile, documents, rag, history } from '../utils/api';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [user, setUser] = useState(null);
  const [docs, setDocs] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(5);
  const navigate = useNavigate();

  useEffect(() => {
    loadProfile();
    loadDocuments();
    loadHistory();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await profile.get();
      setUser(res.data.data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDocuments = async () => {
    try {
      const res = await documents.list();
      setDocs(res.data.data?.documents || []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await history.get();
      setChatHistory(res.data.data?.history || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    for (let file of files) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        await rag.upload(formData);
      } catch (err) {
        console.error(err);
      }
    }
    loadDocuments();
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer('');
    setSources([]);

    try {
      const res = await rag.query(question, topK, null);
      setAnswer(res.data.data?.answer || 'No answer');
      setSources(res.data.data?.sources || []);
      loadHistory();
    } catch (err) {
      setAnswer('Error: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const handleDeleteDoc = async (doc) => {
    try {
      await documents.delete(doc);
      loadDocuments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#F8F9FB' }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.username || 'User'}</h1>
          <p className="text-gray-500 mt-1">Manage your documents and chat with AI</p>
        </div>
        <Button variant="secondary" onClick={handleLogout}>Logout</Button>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-3 mb-6 overflow-x-auto">
        {['chat', 'documents', 'history', 'profile'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={activeTab === tab ? { background: 'linear-gradient(to right, #A5D8FF, #CDB4FF)' } : {}}
            className={`px-6 py-2 rounded-xl font-medium transition-all whitespace-nowrap ${
              activeTab === tab ? 'text-white' : 'bg-white/60'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'chat' && <ChatTab question={question} setQuestion={setQuestion} handleAsk={handleAsk} loading={loading} answer={answer} sources={sources} handleUpload={handleUpload} topK={topK} setTopK={setTopK} />}
        {activeTab === 'documents' && <DocumentsTab docs={docs} handleDeleteDoc={handleDeleteDoc} />}
        {activeTab === 'history' && <HistoryTab chatHistory={chatHistory} />}
        {activeTab === 'profile' && <ProfileTab user={user} />}
      </motion.div>
    </div>
  );
};

// Chat Tab Component
const ChatTab = ({ question, setQuestion, handleAsk, loading, answer, sources, handleUpload, topK, setTopK }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <BentoCard>
      <h3 className="text-xl font-semibold mb-4">📤 Upload PDFs</h3>
      <input type="file" multiple accept=".pdf" onChange={handleUpload} className="w-full p-3 rounded-xl bg-white/50 border border-white/30 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-blue-600 file:font-medium" style={{ fileButtonBackground: 'rgba(165, 216, 255, 0.2)' }} />
    </BentoCard>

    <BentoCard>
      <h3 className="text-xl font-semibold mb-4">💬 Ask Questions</h3>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask anything from your documents..."
        className="w-full p-3 rounded-xl bg-white/50 border border-white/30 focus:outline-none focus:ring-2 mb-3 h-24 resize-none"
        style={{ focusRingColor: 'rgba(165, 216, 255, 0.5)' }}
      />
      <div className="flex items-center gap-3 mb-3">
        <label className="text-sm">Context: {topK}</label>
        <input type="range" min="1" max="10" value={topK} onChange={(e) => setTopK(e.target.value)} className="flex-1" />
      </div>
      <Button onClick={handleAsk} disabled={loading} className="w-full">
        {loading ? 'Thinking...' : 'Ask AI'}
      </Button>
    </BentoCard>

    {answer && (
      <BentoCard span={2}>
        <h3 className="text-xl font-semibold mb-4">✨ Answer</h3>
        <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: answer.replace(/\n/g, '<br>') }} />
        {sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="font-medium mb-2">Sources:</p>
            <ul className="text-sm text-gray-600 space-y-1">
              {sources.map((src, i) => <li key={i}>• {src}</li>)}
            </ul>
          </div>
        )}
      </BentoCard>
    )}
  </div>
);

// Documents Tab Component
const DocumentsTab = ({ docs, handleDeleteDoc }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {docs.length === 0 ? (
      <BentoCard span={3}>
        <p className="text-center text-gray-500">No documents uploaded yet</p>
      </BentoCard>
    ) : (
      docs.map((doc) => (
        <BentoCard key={doc}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <span className="text-2xl mb-2 block">📄</span>
              <p className="text-sm font-medium truncate">{doc}</p>
            </div>
            <Button variant="danger" onClick={() => handleDeleteDoc(doc)} className="!px-3 !py-1 text-sm">Delete</Button>
          </div>
        </BentoCard>
      ))
    )}
  </div>
);

// History Tab Component
const HistoryTab = ({ chatHistory }) => (
  <div className="space-y-4">
    {chatHistory.length === 0 ? (
      <BentoCard>
        <p className="text-center text-gray-500">No conversations yet</p>
      </BentoCard>
    ) : (
      chatHistory.slice(-10).reverse().map((chat, i) => (
        <BentoCard key={i}>
          <p className="font-medium mb-2">Q: {chat.question}</p>
          <p className="text-sm text-gray-600">A: {chat.answer.substring(0, 200)}...</p>
        </BentoCard>
      ))
    )}
  </div>
);

// Profile Tab Component
const ProfileTab = ({ user }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <BentoCard>
      <h3 className="text-xl font-semibold mb-4">👤 Profile Info</h3>
      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-500 uppercase">Username</p>
          <p className="font-medium">{user?.username}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">Email</p>
          <p className="font-medium">{user?.email}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">Member Since</p>
          <p className="font-medium">{user?.created_at?.substring(0, 10)}</p>
        </div>
      </div>
    </BentoCard>

    <BentoCard>
      <h3 className="text-xl font-semibold mb-4">📊 Statistics</h3>
      <div className="space-y-3">
        <div className="flex justify-between items-center p-3 rounded-xl" style={{ backgroundColor: 'rgba(165, 216, 255, 0.1)' }}>
          <span>Queries Used</span>
          <span className="font-bold">{user?.queries_used || 0}</span>
        </div>
        <div className="flex justify-between items-center p-3 rounded-xl" style={{ backgroundColor: 'rgba(184, 242, 230, 0.1)' }}>
          <span>Uploads Used</span>
          <span className="font-bold">{user?.uploads_used || 0}</span>
        </div>
      </div>
    </BentoCard>
  </div>
);

export default Dashboard;
