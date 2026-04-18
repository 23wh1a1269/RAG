import { motion } from 'framer-motion';

const BentoCard = ({ children, className = '', span = 1 }) => {
  return (
    <motion.div
      className={`bento-card ${className}`}
      style={{ gridColumn: `span ${span}` }}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
};

export default BentoCard;
