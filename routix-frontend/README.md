# Routix Frontend - AI Thumbnail Generator

A modern, glassmorphic UI for AI-powered YouTube thumbnail generation with a ChatGPT-like interface.

## 🎨 Design Features

### Visual Style
- **Glassmorphic Cards**: Beautiful transparent cards with backdrop blur
- **Animated Gradients**: Smooth, moving gradient backgrounds
- **Modern Animations**: Professional floating, pulse, and transition effects
- **Responsive Design**: Perfect on desktop, tablet, and mobile

### Key Pages
1. **Landing Page**: Hero section with glassmorphic input and animated logo
2. **Chat Interface**: ChatGPT-style conversation for thumbnail generation
3. **Progress Tracking**: Real-time AI generation progress with status updates

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Run development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## 🎯 Key Components

### Landing Page
- Glassmorphic hero section with animated gradient
- Large input field with glass effect
- Floating logo animation
- Feature pills

### Chat Interface
- Real-time message display
- Glassmorphic message bubbles
- File upload with preview
- Typing indicators

### Progress Tracking
- Animated status badges
- Gradient progress bars
- Real-time generation updates
- Success/error states

## 🎨 Styling System

### CSS Classes

#### Glassmorphic Effects
- `.glass-card` - Main glassmorphic card
- `.glass-card-dark` - Darker variant
- `.glass-input` - Input with glass effect

#### Gradients
- `.gradient-bg-main` - Main app gradient
- `.gradient-bg-purple` - Purple gradient
- `.gradient-bg-blue` - Blue gradient
- `.animated-gradient` - Moving gradient

#### Animations
- `.float-animation` - Smooth floating
- `.hover-lift` - Hover elevation
- `.status-badge` - Pulsing status indicator
- `.smooth-transition` - Smooth transitions

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Touch-friendly targets (44px minimum)
- Optimized animations for mobile

## 🎭 Color Palette

- **Primary**: Blue (#667eea) to Purple (#764ba2)
- **Success**: Green (#10b981)
- **Error**: Red (#ef4444)
- **Warning**: Yellow (#f59e0b)
- **Glass**: White with 70-90% opacity

## 🔧 Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State**: Zustand
- **HTTP**: Axios + React Query

## 📦 Project Structure

```
src/
├── app/                 # Next.js app directory
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   ├── globals.css     # Global styles
│   └── chat/           # Chat pages
├── components/         # React components
│   ├── landing-page.tsx
│   └── chat/          # Chat components
├── hooks/             # Custom React hooks
├── lib/               # Utilities and API
└── types/             # TypeScript types
```

## 🎯 Features

### Implemented
- ✅ Glassmorphic UI design
- ✅ Animated gradients
- ✅ Chat interface
- ✅ Progress tracking
- ✅ Responsive design
- ✅ Mobile optimizations
- ✅ Smooth animations
- ✅ Status indicators

### Coming Soon
- 🔲 Dark mode
- 🔲 Custom themes
- 🔲 Advanced animations
- 🔲 Sound effects

## 🌐 Browser Support

- Chrome/Edge 88+
- Firefox 94+
- Safari 15.4+
- Mobile browsers

## ⚡ Performance

- CSS animations for smooth 60fps
- Lazy loading for components
- Optimized bundle size
- Efficient re-renders

## 🔒 Security

- Input sanitization
- XSS protection
- CSRF tokens
- Secure API calls

## 📝 Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is proprietary software.

## 👥 Team

Developed by the Routix Team

## 📞 Support

For support, email support@routix.ai

---

**Made with ❤️ using modern web technologies**
