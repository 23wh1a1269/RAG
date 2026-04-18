# RAG React Frontend

Modern React frontend with Apple-inspired design for the RAG PDF Chat application.

## Features

- ✨ Apple-inspired minimal design
- 🎨 Bento grid layout
- 💎 Glassmorphism effects
- 🎭 Framer Motion animations
- 🎨 TailwindCSS styling
- 📱 Fully responsive

## Setup

```bash
cd rag-react
npm install
npm run dev
```

The app will run on `http://localhost:5173`

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── BentoCard.jsx
│   ├── Button.jsx
│   ├── Input.jsx
│   └── Modal.jsx
├── pages/           # Page components
│   ├── Login.jsx
│   └── Dashboard.jsx
├── utils/           # Utilities
│   └── api.js       # API client
├── App.jsx          # Main app component
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## Color Palette

- Background: `#F8F9FB`, `#F3F4F6`
- Accent Blue: `#A5D8FF`
- Accent Lavender: `#CDB4FF`
- Accent Mint: `#B8F2E6`
- Accent Peach: `#FFD6A5`
- Text: `#1F2937`

## Components

### BentoCard
Glassmorphic card with hover animations
```jsx
<BentoCard span={2}>Content</BentoCard>
```

### Button
Animated button with variants
```jsx
<Button variant="primary" onClick={handleClick}>Click</Button>
```

### Input
Styled input with glassmorphism
```jsx
<Input placeholder="Enter text" value={value} onChange={onChange} />
```

### Modal
Animated modal with backdrop blur
```jsx
<Modal isOpen={isOpen} onClose={onClose} title="Title">Content</Modal>
```

## Build

```bash
npm run build
```

Output will be in `dist/` folder.

## Backend Connection

Make sure the backend is running on `http://localhost:8000`

Update `src/utils/api.js` if using a different URL.
