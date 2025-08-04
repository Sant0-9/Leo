# 🧠 Leo AI Assistant

A modern, full-stack AI assistant with React frontend and FastAPI backend, featuring real-time chat, calendar integration, and smart productivity tools.

## ✨ Features

- 🤖 **AI-Powered Chat** - Intelligent conversations using OpenAI GPT
- 🌙 **Dark/Light Mode** - Beautiful themes with smooth transitions
- 📅 **Calendar Integration** - Google Calendar support with interactive cards
- ⚙️ **User Settings** - Customizable preferences and configurations
- 🔔 **Real-time Notifications** - Toast notifications and WebSocket updates
- 💾 **Persistent Memory** - Conversation history and long-term storage
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Leo
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Install dependencies:**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install && cd ..
   ```

4. **Start Leo:**
   ```bash
   # Full system (recommended)
   python3 start_leo_full.py
   
   # Or start components separately:
   python3 start_leo_backend.py  # Backend only
   python3 start_leo_frontend.py # Frontend only
   ```

5. **Access Leo:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
Leo/
├── agents/           # AI agent logic
├── backend/          # FastAPI backend services
├── frontend/         # React frontend
├── utils/            # Shared utilities
└── chroma_db/        # Vector database storage
```

### Backend (FastAPI)
- RESTful API endpoints
- WebSocket for real-time updates
- ChromaDB for vector storage
- Google Services integration
- Memory management system

### Frontend (React)
- Modern React 19 with hooks
- Tailwind CSS for styling
- Component-based architecture
- Real-time WebSocket integration
- Responsive design

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Features Configuration
- **AI Model**: GPT-3.5 Turbo by default
- **Memory**: Persistent conversation storage
- **Themes**: Auto-detect system preference
- **Notifications**: Customizable duration and types

## 🎯 Usage

### Chat with Leo
1. Open http://localhost:3000
2. Switch between Agent and Assistant modes
3. Start chatting with Leo
4. Access settings via the gear icon

### Calendar Integration
1. Click on calendar cards to view events
2. Configure Google Calendar in settings
3. Interactive event details and timing

### Customization
1. Toggle dark/light theme
2. Adjust notification preferences
3. Configure memory retention
4. Export/import settings

## 🛠️ Development

### Project Structure
```
├── agents/smart_assistant.py    # Core AI logic
├── backend_main.py              # FastAPI server
├── frontend/src/
│   ├── components/              # React components
│   ├── pages/                   # Main pages
│   ├── services/               # API services
│   └── hooks/                  # Custom hooks
└── utils/
    ├── memory_manager.py       # Memory system
    └── mode_manager.py         # Mode switching
```

### Adding Features
1. Backend: Add endpoints to `backend_main.py`
2. Frontend: Create components in `frontend/src/components/`
3. Services: Add API calls to `frontend/src/services/api.js`

### API Endpoints
- `GET /api/health` - System health
- `POST /api/chat/send` - Send message
- `GET /api/chat/history` - Chat history
- `WS /ws` - WebSocket connection

## 🚀 Deployment

### Production Build
```bash
# Build frontend
cd frontend && npm run build

# Start production backend
python3 -m uvicorn backend_main:app --host 0.0.0.0 --port 8000
```

### Docker (Optional)
```bash
# Build and run with Docker
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

**Leo AI Assistant** - Built with ❤️ using React, FastAPI, and OpenAI