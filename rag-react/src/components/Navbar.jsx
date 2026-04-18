import { motion } from 'framer-motion';

const Navbar = ({ username, onLogout }) => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-3xl px-6 py-4 mb-8 flex justify-between items-center"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-accent-blue to-accent-lavender rounded-xl flex items-center justify-center">
          <span className="text-xl">📄</span>
        </div>
        <div>
          <h2 className="font-semibold">RAG GPT</h2>
          <p className="text-xs text-gray-500">@{username}</p>
        </div>
      </div>
      <button
        onClick={onLogout}
        className="px-4 py-2 rounded-xl bg-white/50 hover:bg-white/80 transition-all text-sm font-medium"
      >
        Logout
      </button>
    </motion.nav>
  );
};

export default Navbar;
