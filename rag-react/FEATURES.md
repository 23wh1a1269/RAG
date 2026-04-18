# 🎨 React Frontend Features

## Design System

### 🎯 Apple-Inspired Aesthetic
- Minimal, clean layouts
- Soft shadows and rounded corners
- Subtle gradients
- Generous whitespace
- Inter font family

### 💎 Glassmorphism
```css
background: rgba(255, 255, 255, 0.6)
backdrop-filter: blur(16px)
border: 1px solid rgba(255, 255, 255, 0.3)
```

### 🎨 Color Palette
```
Background:  #F8F9FB, #F3F4F6
Blue:        #A5D8FF (calm, trustworthy)
Lavender:    #CDB4FF (elegant, creative)
Mint:        #B8F2E6 (fresh, positive)
Peach:       #FFD6A5 (warm, friendly)
Text:        #1F2937 (readable)
```

## Components

### BentoCard
```jsx
<BentoCard span={2}>
  <h3>Title</h3>
  <p>Content</p>
</BentoCard>
```
- Glassmorphic background
- Hover lift animation
- Responsive grid span
- Rounded corners (24px)

### Button
```jsx
<Button variant="primary" onClick={action}>
  Click Me
</Button>
```
Variants:
- `primary`: Gradient blue → lavender
- `secondary`: White with border
- `danger`: Red background

Animations:
- Hover: scale(1.02)
- Tap: scale(0.98)

### Input
```jsx
<Input 
  placeholder="Enter text"
  value={value}
  onChange={onChange}
/>
```
- Glass background
- Focus ring animation
- Smooth transitions

### Modal
```jsx
<Modal isOpen={open} onClose={close} title="Title">
  Content
</Modal>
```
- Backdrop blur
- Scale + fade animation
- Click outside to close

## Pages

### Login Page
- Tab switching (Login/Signup)
- Form validation
- Error handling
- Gradient background
- Smooth animations

### Dashboard
Bento grid with 4 tabs:

**Chat Tab**
- Upload PDFs card
- Ask questions card
- Answer display (2-column span)
- Context slider

**Documents Tab**
- Grid of document cards
- Delete functionality
- Empty state message

**History Tab**
- Conversation list
- Expandable answers
- Reverse chronological

**Profile Tab**
- User info card
- Statistics card

## Animations

### Page Transitions
```jsx
initial={{ opacity: 0, x: 20 }}
animate={{ opacity: 1, x: 0 }}
transition={{ duration: 0.3 }}
```

### Card Hover
```jsx
whileHover={{ y: -4, scale: 1.01 }}
transition={{ duration: 0.2 }}
```

### Button Interaction
```jsx
whileHover={{ scale: 1.02 }}
whileTap={{ scale: 0.98 }}
```

### Modal
```jsx
initial={{ opacity: 0, scale: 0.9, y: 20 }}
animate={{ opacity: 1, scale: 1, y: 0 }}
exit={{ opacity: 0, scale: 0.9, y: 20 }}
```

## Responsive Design

### Breakpoints
- Mobile: < 640px (single column)
- Tablet: 640px - 1024px (2 columns)
- Desktop: > 1024px (full Bento grid)

### Grid System
```jsx
grid-cols-1 md:grid-cols-2 lg:grid-cols-3
```

## Tech Stack

- **React 19**: Latest React features
- **Vite**: Lightning-fast HMR
- **TailwindCSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **React Router**: Client-side routing
- **Axios**: HTTP client

## Performance

- Fast HMR with Vite
- Optimized bundle size
- Lazy loading ready
- Tree-shaking enabled
- Production build optimization

## Accessibility

- Semantic HTML
- Keyboard navigation
- Focus indicators
- ARIA labels ready
- Screen reader friendly

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android
