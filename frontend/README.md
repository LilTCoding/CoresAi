# CoresAI React Frontend

A modern, responsive React frontend for the CoresAI Advanced AI System built with TypeScript, Tailwind CSS, and Framer Motion.

## 🚀 Features

- **Modern React Architecture** - Built with React 18, TypeScript, and modern hooks
- **Beautiful UI/UX** - Sleek design with Tailwind CSS and Framer Motion animations
- **Multi-Backend Integration** - Connects to both production and streaming backends
- **Real-time Capabilities** - Live health monitoring and streaming responses
- **Responsive Design** - Works perfectly on desktop and mobile devices
- **PWA Ready** - Progressive Web App capabilities built-in

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **Axios** for HTTP requests
- **React Hot Toast** for notifications
- **Heroicons** for icons

## 📱 Pages & Features

### Dashboard
- System overview and health monitoring
- Feature showcase cards
- Backend status indicators
- Real-time health checks

### AI Chat
- Interactive conversation interface
- Real-time message exchange
- Message history and context
- Quick action suggestions

### Web Search
- AI-powered web search interface
- Real-time search results
- Intelligent summaries
- Relevance scoring

### Structured Streaming
- Advanced streaming responses
- Multiple output modes (object, array, no-schema)
- Schema auto-detection
- Real-time chunk visualization

### Creative Software Knowledge
- Expert knowledge for Photoshop, Blender, VEGAS Pro
- Tabbed interface for tools, workspaces, techniques
- Interactive software cards
- Comprehensive knowledge base

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm 8+
- CoresAI backends running (production on 8080, streaming on 8081)

### Installation

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_PRODUCTION_API_URL=http://localhost:8080
REACT_APP_STREAMING_API_URL=http://localhost:8081
```

## 🏗️ Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── manifest.json       # PWA manifest
├── src/
│   ├── components/         # Reusable React components
│   │   ├── Navbar.tsx     # Navigation bar
│   │   └── BackendStatus.tsx # Backend health status
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx  # Main dashboard
│   │   ├── Chat.tsx       # AI chat interface
│   │   ├── WebSearch.tsx  # Web search page
│   │   ├── StreamingDemo.tsx # Streaming demo
│   │   └── CreativeSoftware.tsx # Creative software knowledge
│   ├── services/          # API services
│   │   └── api.ts         # Backend API integration
│   ├── App.tsx            # Main app component
│   ├── index.tsx          # App entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind configuration
└── tsconfig.json          # TypeScript configuration
```

## 🔧 Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## 🌐 API Integration

The frontend integrates with two CoresAI backends:

### Production Backend (Port 8080)
- Traditional chat endpoint
- Web search functionality
- Server management
- Health monitoring

### Streaming Backend (Port 8081)
- Structured streaming responses
- Schema detection
- Creative software knowledge
- Real-time data streaming

## 🎨 UI Components

### Interactive Elements
- Animated navigation bar
- Real-time health indicators
- Loading states and animations
- Toast notifications
- Modal dialogs

### Design System
- Consistent color palette (cyan/purple gradients)
- Typography hierarchy
- Spacing and layout grid
- Glass morphism effects
- Smooth transitions

## 📱 Responsive Design

- **Mobile First** - Optimized for mobile devices
- **Breakpoints** - sm, md, lg, xl screen sizes
- **Touch Friendly** - Large tap targets and gestures
- **Performance** - Optimized for all device types

## 🚀 Deployment to Vercel

### Option 1: Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd frontend
   vercel --prod
   ```

### Option 2: Git Integration

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add React frontend"
   git push origin main
   ```

2. **Import in Vercel:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import from GitHub
   - Select your repository
   - Configure build settings:
     - Framework Preset: Create React App
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `build`

3. **Environment Variables:**
   Add in Vercel dashboard:
   ```
   REACT_APP_PRODUCTION_API_URL=https://your-production-backend.vercel.app
   REACT_APP_STREAMING_API_URL=https://your-streaming-backend.vercel.app
   ```

### Option 3: Vercel v0 Integration

You can also use Vercel's v0 tool to generate additional UI components:

1. **Generate components:**
   ```bash
   npx v0@latest add [component-name]
   ```

2. **Customize and integrate** the generated components into your app

## 🔒 Production Considerations

### Backend URLs
Update the API URLs in `src/services/api.ts` for production:

```typescript
const PRODUCTION_API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-backend.vercel.app' 
  : 'http://localhost:8080';
```

### CORS Configuration
Ensure your backends allow requests from your Vercel domain:

```python
# In your FastAPI backends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables
Set production environment variables in Vercel dashboard for:
- Backend API URLs
- API keys (if needed)
- Feature flags

## 🎯 Performance Optimizations

- **Code Splitting** - Route-based code splitting
- **Lazy Loading** - Components loaded on demand
- **Image Optimization** - Optimized images and icons
- **Bundle Analysis** - Webpack bundle analyzer
- **Caching** - API response caching

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Errors:**
   - Check if backends are running on correct ports
   - Verify CORS configuration
   - Check network connectivity

2. **Build Errors:**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npm run type-check`

3. **Styling Issues:**
   - Ensure Tailwind is properly configured
   - Check for conflicting CSS rules
   - Verify PostCSS configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the main CoresAI documentation
- Review the API endpoints documentation
- Check the backend status and logs

---

**CoresAI Frontend v4.1.0** - Built with ❤️ using React and deployed on Vercel 