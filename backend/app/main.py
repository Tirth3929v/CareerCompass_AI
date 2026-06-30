"""FastAPI server for CareerCompass AI.

Exposes the multi-agent career guidance system via REST API endpoints.
Handles session management, CORS, rate limiting, and MongoDB lifecycle.
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError

from app.agents.graph import get_root_agent
from app.config import settings
from app.db.connection import MongoConnection
from app.db.repositories import UserProfileRepository
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.mock_helper import generate_mock_response
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SessionState,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ADK Session & Runner Setup ---

APP_NAME = "careercompass_ai"
session_service = InMemorySessionService()
root_agent: Agent = get_root_agent()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# --- Application Lifecycle ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("🚀 Starting CareerCompass AI Backend...")
    try:
        await MongoConnection.connect()
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}. Running without persistence.")

    logger.info(f"🤖 Agent graph initialized: {root_agent.name}")
    logger.info(f"🔑 Gemini model: {settings.gemini_model}")
    logger.info(f"🛡️ Rate limit: {settings.rate_limit_per_day} requests/day")

    yield

    # Shutdown
    await MongoConnection.disconnect()
    logger.info("👋 CareerCompass AI Backend shut down.")


# --- FastAPI App ---

app = FastAPI(
    title="CareerCompass AI",
    description="Multi-agent career guidance and skill verification platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.add_middleware(RateLimiterMiddleware, max_requests_per_day=settings.rate_limit_per_day)


# --- Helper Functions ---

async def _get_or_create_session(session_id: str, user_id: str):
    """Get an existing ADK session or create a new one."""
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if session is None:
        # Try to load profile context from MongoDB
        profile_context = ""
        try:
            profile_context = await UserProfileRepository.get_profile_summary(session_id)
        except Exception:
            pass

        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={
                "mode": "chat",
                "target_career": None,
                "claimed_skills": [],
                "verified_scores": [],
                "profile_context": profile_context,
            },
        )
    return session


def _parse_agent_response(response_text: str) -> dict:
    """Parse structured markers from agent responses.

    Agents embed structured data using pipe-delimited markers like:
    VERIFICATION_TRIGGER|career|skill1|skill2|...
    SCORE_SUBMITTED|skill|score|feedback|is_last|...
    ANALYSIS_COMPLETE|career|score|STRENGTHS:...|GAPS:...|...
    ROADMAP_COMPLETE|{json}
    """
    result = {"mode": "chat", "message": response_text, "data": None}

    # Check if the response contains or is a JSON challenge question
    cleaned_text = response_text.strip()
    json_str = None
    if "```json" in cleaned_text:
        try:
            json_str = cleaned_text.split("```json")[1].split("```")[0].strip()
        except Exception:
            pass
    elif cleaned_text.startswith("{") and cleaned_text.endswith("}"):
        json_str = cleaned_text

    if json_str:
        try:
            data = json.loads(json_str)
            if "question" in data and "type" in data:
                result["mode"] = "verification"
                result["data"] = data
                result["message"] = "Solve the technical challenge below:"
                return result
        except Exception:
            pass

    if "VERIFICATION_TRIGGER|" in response_text:
        parts = response_text.split("VERIFICATION_TRIGGER|")[1].split("|")
        result["mode"] = "verification"
        result["data"] = {
            "target_career": parts[0] if len(parts) > 0 else "",
            "claimed_skills": [p for p in parts[1:-1] if p and not p.startswith("Verification")],
        }
        # Clean message — remove the marker from display
        result["message"] = response_text.split("VERIFICATION_TRIGGER|")[0].strip()
        if not result["message"]:
            result["message"] = parts[-1] if parts else "Starting verification..."

    elif "SCORE_SUBMITTED|" in response_text:
        parts = response_text.split("SCORE_SUBMITTED|")[1].split("|")
        result["mode"] = "verification"
        result["data"] = {
            "skill_name": parts[0] if len(parts) > 0 else "",
            "score": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0,
            "feedback": parts[2] if len(parts) > 2 else "",
            "is_last": parts[3].lower() == "true" if len(parts) > 3 else False,
        }
        result["message"] = response_text.split("SCORE_SUBMITTED|")[0].strip()
        if not result["message"]:
            result["message"] = parts[-1] if parts else "Score recorded."

    elif "ANALYSIS_COMPLETE|" in response_text:
        result["mode"] = "analysis"
        result["message"] = response_text.split("ANALYSIS_COMPLETE|")[0].strip()
        if not result["message"]:
            result["message"] = "Analysis complete! Here are your verified skill scores."

    elif "ROADMAP_COMPLETE|" in response_text:
        result["mode"] = "roadmap"
        json_str = response_text.split("ROADMAP_COMPLETE|")[1]
        try:
            result["data"] = json.loads(json_str)
        except json.JSONDecodeError:
            result["data"] = None
        result["message"] = response_text.split("ROADMAP_COMPLETE|")[0].strip()
        if not result["message"]:
            result["message"] = "Your personalized career roadmap is ready!"

    return result


# --- API Endpoints ---


@app.get("/")
def read_root():
    """Root endpoint returning service status."""
    return {"status": "CareerCompass API is running!"}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Render deployment monitoring."""
    return HealthResponse()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — processes messages through the multi-agent system.

    The agent graph automatically routes between Counselor, Verifier,
    Analyzer, and Roadmap agents based on conversation state.
    """
    print(" === DEBUG 1: Received request from frontend ===")
    print(f"User Message: {request.message} | Mode: {request.mode}")
    
    # -----------------------------------------
    # MOCK MODE BYPASS
    # -----------------------------------------
    if getattr(settings, 'mock_mode', False):
        print(" === DEBUG: MOCK MODE ACTIVATED ===")
        # Add a tiny artificial delay so the UI loading animation still looks natural
        await asyncio.sleep(1.5) 
        return generate_mock_response(request)

    # -----------------------------------------
    # LIVE LLM MODE (With Failsafes)
    # -----------------------------------------
    print(" === DEBUG 2: About to invoke the Agent Graph ===")
    try:
        user_id = f"user_{request.session_id}"

        # Get or create ADK session
        session = await _get_or_create_session(request.session_id, user_id)

        # Build the user message content
        user_message = request.message
        if request.mode == "challenge_response":
            user_message = f"[CHALLENGE RESPONSE] {request.message}"

        # Inject profile context if this is a returning user
        profile_context = session.state.get("profile_context", "")
        if profile_context and len(session.events) <= 1:
            # Prepend context only on first interaction
            user_message = f"[RETURNING USER CONTEXT]\n{profile_context}\n\n[USER MESSAGE]\n{user_message}"

        # Create the user content
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        )

        response_text = ""
        
        async def run_graph():
            nonlocal response_text
            async for event in runner.run_async(
                user_id=user_id,
                session_id=request.session_id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text or ""

        # Wrap the live LLM call in a strict 15-second timeout
        await asyncio.wait_for(run_graph(), timeout=15.0)
        print(" === DEBUG 3: Agent Graph responded successfully ===")

        if not response_text:
            response_text = "I'm processing your request. Please give me a moment..."

        # Parse structured data from agent response
        parsed = _parse_agent_response(response_text)

        # Persist to MongoDB in background
        try:
            if parsed["mode"] == "verification" and parsed.get("data"):
                data = parsed["data"]
                if "target_career" in data:
                    await UserProfileRepository.update_target_career(
                        request.session_id,
                        data["target_career"],
                        data.get("claimed_skills", []),
                    )
        except Exception as e:
            logger.warning(f"MongoDB persistence failed: {e}")

        # Build response
        response = ChatResponse(
            message=parsed["message"],
            mode=parsed["mode"],
        )

        # Attach structured data based on mode
        if parsed["mode"] == "verification" and parsed.get("data"):
            data = parsed["data"]
            if "question" in str(data):
                try:
                    response.challenge_data = data
                except Exception:
                    pass

        return response

    except ClientError as ce:
        print(f" !!! DEBUG ERROR: Gemini API Client Error: {ce} !!!")
        if "429" in str(ce) or "RESOURCE_EXHAUSTED" in str(ce):
            return ChatResponse(
                message="Oops! My AI brain is currently experiencing a high volume of requests (Google API Free Tier Quota Exceeded). Please wait a minute and try again!",
                mode="chat"
            )
        raise HTTPException(status_code=500, detail="An error occurred communicating with the AI service.")

    except asyncio.TimeoutError:
        print(" !!! DEBUG ERROR: Agent Graph timed out! !!!")
        return ChatResponse(
            message="My circuits are a bit overloaded and taking too long to think! Could you simplify your request?", 
            mode="chat"
        )

    except Exception as e:
        print(f" !!! DEBUG ERROR: Graph crashed with unexpected error: {e} !!!")
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            message="Something went wrong behind the scenes. Let's try starting over!",
            mode="chat"
        )


@app.get("/api/session/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """Retrieve the current state of a user's session."""
    try:
        profile = await UserProfileRepository.get_or_create_profile(session_id)
        return SessionState(
            session_id=session_id,
            current_mode=profile.get("current_mode", "chat"),
            target_career=profile.get("target_career"),
            claimed_skills=profile.get("claimed_skills", []),
            overall_score=profile.get("overall_score"),
        )
    except Exception as e:
        logger.error(f"Session retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roadmap/{session_id}")
async def get_roadmap(session_id: str):
    """Retrieve the generated roadmap for a session."""
    try:
        profile = await UserProfileRepository.get_or_create_profile(session_id)
        roadmap = profile.get("roadmap")
        if not roadmap:
            raise HTTPException(
                status_code=404,
                detail="No roadmap generated yet for this session.",
            )
        return {"session_id": session_id, "roadmap": roadmap}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Roadmap retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
