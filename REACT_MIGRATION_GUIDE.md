# 🎨 React Frontend Migration Guide

## Overview

The RAG PDF Chat application has been converted to a modern React application with:

- **React 19** + **Vite** for fast development
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **Apple-inspired design** with Bento grid layout
- **Glassmorphism** effects
- **Fully responsive** design

## Quick Start

### 1. Navigate to React app
```bash
cd /home/user/Downloads/RAG1/rag-react
```

### 2. Install dependencies (if not already done)
```bash
npm install
```

### 3. Start development server
```bash
npm run dev
```

Or use the startup script:
```bash
cd /home/user/Downloads/RAG1
./start-react.sh
```

### 4. Access the app
Open `http://localhost:5173` in your browser

## Architecture

### Folder Structure
```
rag-react/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── BentoCard.jsx   # Glassmorphic card component
│   │   ├── Button.jsx      # Animated button
│   │   ├── Input.jsx       # Styled input field
│   │   ├── Modal.jsx       # Modal dialog
│   │   └── Navbar.jsx      # Navigation bar
│   ├── pages/              # Page components
│   │   ├── Login.jsx       # Login/Signup page
│   │   └── Dashboard.jsx   # Main dashboard with Bento layout
│   ├── utils/              # Utility functions
│   │   └── api.js          # API client with axios
│   ├── App.jsx             # Main app with routing
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles + Tailwind
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── package.json            # Dependencies
```

## Design System

### Color Palette
```javascript
Background:
  - Primary: #F8F9FB
  - Secondary: #F3F4F6

Accent Colors:
  - Blue: #A5D8FF (soft, calming)
  - Lavender: #CDB4FF (elegant)
  - Mint: #B8F2E6 (fresh)
  - Peach: #FFD6A5 (warm)

Text:
  - Primary: #1F2937 (dark gray)
```

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Fallback**: system-ui, -apple-system, sans-serif

### Components

#### BentoCard
Glassmorphic card with hover animations
```jsx
<BentoCard span={2} className="custom-class">
  <h3>Title</h3>
  <p>Content</p>
</BentoCard>
```

Properties:
- `span`: Grid column span (1-2)
- `className`: Additional CSS classes
- Hover effect: Lifts up with scale animation

#### Button
Animated button with variants
```jsx
<Button 
  variant="primary"    // primary | secondary | danger
  onClick={handleClick}
  disabled={false}
>
  Click Me
</Button>
```

Variants:
- `primary`: Gradient blue to lavender
- `secondary`: White with border
- `danger`: Red background

#### Input
Glassmorphic input field
```jsx
<Input
  type="text"
  placeholder="Enter text"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

Features:
- Backdrop blur effect
- Focus ring animation
- Smooth transitions

#### Modal
Animated modal with backdrop
```jsx
<Modal 
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Modal Title"
>
  <p>Modal content</p>
</Modal>
```

Features:
- Backdrop blur
- Scale + fade animation
- Click outside to close

## Pages

### Login Page
- Tab switching between Login/Signup
- Form validation
- Error handling
- Smooth animations
- Gradient background

### Dashboard Page
Bento grid layout with 4 tabs:

1. **Chat Tab**
   - Upload PDFs card
   - Ask questions card
   - Answer display (spans 2 columns)
   - Context slider (top_k)

2. **Documents Tab**
   - Grid of document cards
   - Delete functionality
   - Empty state

3. **History Tab**
   - List of past conversations
   - Truncated answers
   - Reverse chronological order

4. **Profile Tab**
   - User information card
   - Statistics card (queries, uploads)

## API Integration

### API Client (`src/utils/api.js`)

```javascript
import { auth, profile, documents, rag, history } from './utils/api';

// Authentication
await auth.login(username, password);
await auth.signup(username, email, password);
await auth.changePassword(old_password, new_password);

// Profile
await profile.get();
await profile.update(new_username, new_email);

// Documents
await documents.list();
await documents.delete(docName);

// RAG
await rag.upload(formData);
await rag.query(question, top_k, selected_documents);

// History
await history.get();
```

### Authentication Flow
1. User logs in → Token stored in localStorage
2. Token automatically added to all requests via interceptor
3. Protected routes check for token
4. Logout clears localStorage

## Styling

### Tailwind Classes

Custom classes defined in `index.css`:
```css
.glass-card {
  @apply bg-white/60 backdrop-blur-lg border border-white/30 shadow-lg;
}

.bento-card {
  @apply glass-card rounded-3xl p-6 transition-all duration-300 
         hover:shadow-xl hover:-translate-y-1;
}
```

### Responsive Design
- Mobile: Single column layout
- Tablet: 2 column grid
- Desktop: Full Bento grid

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

## Animations

### Framer Motion

Page transitions:
```jsx
<motion.div
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  transition={{ duration: 0.3 }}
>
```

Button interactions:
```jsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
```

Card hover:
```jsx
<motion.div
  whileHover={{ y: -4, scale: 1.01 }}
  transition={{ duration: 0.2 }}
>
```

## Development

### Run Development Server
```bash
npm run dev
```
Runs on `http://localhost:5173` with hot reload

### Build for Production
```bash
npm run build
```
Output in `dist/` folder

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

## Backend Connection

The React app connects to the FastAPI backend at `http://localhost:8000`

To change the API URL, edit `src/utils/api.js`:
```javascript
const API_URL = 'http://your-backend-url:port';
```

## Running Full Stack

### Terminal 1: Backend
```bash
cd /home/user/Downloads/RAG1
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Terminal 2: React Frontend
```bash
cd /home/user/Downloads/RAG1/rag-react
npm run dev
```

### Terminal 3: Qdrant (if not running)
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

## Comparison: Old vs New

| Feature | Old (HTML/CSS/JS) | New (React) |
|---------|------------------|-------------|
| Framework | Vanilla JS | React 19 + Vite |
| Styling | Custom CSS | TailwindCSS |
| Animations | CSS transitions | Framer Motion |
| State Management | DOM manipulation | React hooks |
| Routing | Multiple HTML files | React Router |
| Components | None | Reusable components |
| Build Tool | None | Vite |
| Hot Reload | Manual refresh | Automatic |
| Type Safety | None | JSX validation |
| Code Organization | Scattered | Modular |

## Features Implemented

✅ Login/Signup with tab switching
✅ JWT authentication
✅ Protected routes
✅ PDF upload
✅ AI-powered Q&A
✅ Document management
✅ Chat history
✅ User profile
✅ Glassmorphism effects
✅ Bento grid layout
✅ Smooth animations
✅ Responsive design
✅ Error handling
✅ Loading states

## Next Steps

### Potential Enhancements
- [ ] Dark mode toggle
- [ ] Document preview
- [ ] Advanced search filters
- [ ] Real-time chat updates
- [ ] File drag & drop
- [ ] Markdown rendering for answers
- [ ] Export chat history
- [ ] Multi-language support
- [ ] Progressive Web App (PWA)
- [ ] Accessibility improvements

## Troubleshooting

### Port already in use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Dependencies not installing
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend connection error
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_URL in `src/utils/api.js`

### Build errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [Framer Motion Documentation](https://www.framer.com/motion)
- [React Router Documentation](https://reactrouter.com)

---

**Built with ❤️ using React, Vite, TailwindCSS, and Framer Motion**
