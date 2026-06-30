# 🧭 CareerCompass AI

A multi-agent career guidance and skill verification platform. Students interact with an AI counselor, have their technical skills verified through interactive challenges, and receive a personalized career roadmap.

## Architecture

```
┌─────────────┐    HTTP     ┌──────────────────────────────────────────┐
│  Angular 17  │◄──────────►│          FastAPI Backend                 │
│  SSR (Vercel)│            │                                          │
│              │            │  ┌──────────┐   ┌──────────┐            │
│  • Chat UI   │            │  │Counselor │──►│ Verifier │            │
│  • Challenge │            │  │  Agent   │   │  Agent   │            │
│    Cards     │            │  └────┬─────┘   └────┬─────┘            │
│  • Dashboard │            │       │              │                   │
│  • Roadmap   │            │  ┌────▼─────┐   ┌────▼─────┐            │
│              │            │  │ Analyzer │──►│ Roadmap  │            │
│              │            │  │  Agent   │   │  Agent   │            │
└─────────────┘            │  └──────────┘   └──────────┘            │
                            │                          │               │
                            └──────────────────────────┼───────────────┘
                                                       │
                                                 ┌─────▼─────┐
                                                 │  MongoDB   │
                                                 │  Atlas M0  │
                                                 └───────────┘
```

## Quick Start

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+
- MongoDB Atlas free cluster (or local MongoDB)
- Gemini API key ([ai.google.dev](https://ai.google.dev))

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Edit with your keys
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
ng serve
```

### Environment Variables
| Variable | Description |
|----------|-------------|
| `GOOGLE_GENAI_API_KEY` | Gemini API key from ai.google.dev |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) |
| `RATE_LIMIT_PER_DAY` | Max API requests per IP/day (default: 20) |

## Deployment
- **Frontend**: Vercel (Angular SSR)
- **Backend**: Render (Docker, free tier)

## Tech Stack
- **Frontend**: Angular 17, SSR, RxJS
- **Backend**: FastAPI, Google ADK, Gemini 2.0 Flash
- **Database**: MongoDB Atlas (Free Tier)
- **LLM**: Gemini API (Free Tier)
