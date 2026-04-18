import { motion } from 'framer-motion';

const Button = ({ children, variant = 'primary', onClick, className = '', disabled = false }) => {
  const variants = {
    primary: 'text-white',
    secondary: 'bg-white/80 border border-white/50',
    danger: 'bg-red-500 text-white'
  };

  const primaryStyle = variant === 'primary' ? {
    background: 'linear-gradient(to right, #A5D8FF, #CDB4FF)'
  } : {};

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      style={primaryStyle}
      className={`px-6 py-3 rounded-2xl font-medium transition-all ${variants[variant]} ${className} disabled:opacity-50`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  );
};

export default Button;
