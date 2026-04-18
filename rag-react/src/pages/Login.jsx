import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { auth } from '../utils/api';
import Button from '../components/Button';
import Input from '../components/Input';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', email: '', password: '', password2: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      if (isLogin) {
        const res = await auth.login(formData.username, formData.password);
        if (res.data.success) {
          localStorage.setItem('token', res.data.data.token);
          localStorage.setItem('username', formData.username);
          navigate('/dashboard');
        }
      } else {
        if (formData.password !== formData.password2) {
          setMessage('Passwords don\'t match');
          setLoading(false);
          return;
        }
        const res = await auth.signup(formData.username, formData.email, formData.password);
        if (res.data.success) {
          setMessage('Account created! Please login.');
          setTimeout(() => setIsLogin(true), 2000);
        }
      }
    } catch (err) {
      setMessage(err.response?.data?.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(to bottom right, rgba(165, 216, 255, 0.2), rgba(205, 180, 255, 0.2), rgba(184, 242, 230, 0.2))' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bento-card">
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(to bottom right, #A5D8FF, #CDB4FF)' }}>
              <span className="text-3xl">📄</span>
            </div>
            <h1 className="text-3xl font-bold">RAG GPT</h1>
            <p className="text-gray-500 mt-2">Chat with your documents</p>
          </div>

          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              style={isLogin ? { background: 'linear-gradient(to right, #A5D8FF, #CDB4FF)' } : {}}
              className={`flex-1 py-2 rounded-xl font-medium transition-all ${isLogin ? 'text-white' : 'bg-white/50'}`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              style={!isLogin ? { background: 'linear-gradient(to right, #A5D8FF, #CDB4FF)' } : {}}
              className={`flex-1 py-2 rounded-xl font-medium transition-all ${!isLogin ? 'text-white' : 'bg-white/50'}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            />
            {!isLogin && (
              <Input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            )}
            <Input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
            {!isLogin && (
              <Input
                type="password"
                placeholder="Confirm Password"
                value={formData.password2}
                onChange={(e) => setFormData({ ...formData, password2: e.target.value })}
              />
            )}
            <Button className="w-full" disabled={loading}>
              {loading ? 'Loading...' : isLogin ? 'Login' : 'Create Account'}
            </Button>
          </form>

          {message && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className={`mt-4 text-center text-sm ${message.includes('success') || message.includes('created') ? 'text-green-600' : 'text-red-600'}`}
            >
              {message}
            </motion.p>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
