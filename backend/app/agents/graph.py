"""Multi-Agent Graph Assembly.

Assembles the 4-agent system using Google ADK's orchestration.
Root agent (Counselor) delegates to sub-agents: Verifier, Analyzer, Roadmap.

State transitions: counseling → verification → analysis → roadmap
"""

import os

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.agents.analyzer import ANALYZER_INSTRUCTION, submit_analysis
from app.agents.counselor import COUNSELOR_INSTRUCTION, trigger_verification
from app.agents.roadmap import ROADMAP_INSTRUCTION, submit_roadmap
from app.agents.verifier import (
    VERIFIER_INSTRUCTION,
    generate_challenge,
    submit_score,
)
from app.config import settings


_original_generate = Gemini.generate_content_async

async def _debug_generate(*args, **kwargs):
    print(" === DEBUG LLM: Sending payload to Google Gemini API... ===")
    async for chunk in _original_generate(*args, **kwargs):
        yield chunk
    print(" === DEBUG LLM: Received response from Google Gemini API! ===")

Gemini.generate_content_async = _debug_generate


def _create_model() -> Gemini:
    """Create a Gemini model instance with retry configuration."""
    return Gemini(
        model=settings.gemini_model,
        api_key=settings.google_genai_api_key,
        retry_options=types.HttpRetryOptions(attempts=3),
    )


# --- Sub-Agent Definitions ---

verifier_agent = Agent(
    name="verifier_agent",
    model=_create_model(),
    description=(
        "Skill Verification Specialist. Generates targeted technical challenges "
        "(code, math, logic) to verify a student's claimed skills. Evaluates "
        "responses and assigns verified scores (0-10)."
    ),
    instruction=VERIFIER_INSTRUCTION,
    tools=[submit_score, generate_challenge],
)

analyzer_agent = Agent(
    name="analyzer_agent",
    model=_create_model(),
    description=(
        "Skill Gap Analyst. Takes verified skill scores and compares them "
        "against target career requirements. Produces overall score, "
        "strengths, gaps, and a comprehensive analysis."
    ),
    instruction=ANALYZER_INSTRUCTION,
    tools=[submit_analysis],
)

roadmap_agent = Agent(
    name="roadmap_agent",
    model=_create_model(),
    description=(
        "Career Roadmap Generator. Creates personalized, phased study plans "
        "with free resources, milestones, and timelines based on identified "
        "skill gaps. Output is structured JSON."
    ),
    instruction=ROADMAP_INSTRUCTION,
    tools=[submit_roadmap],
)

# --- Root Agent (Counselor / Orchestrator) ---

counselor_agent = Agent(
    name="counselor_agent",
    model=_create_model(),
    description=(
        "Career Counselor and Orchestrator. Gathers student information, "
        "then delegates to specialized sub-agents for verification, "
        "analysis, and roadmap generation."
    ),
    instruction=COUNSELOR_INSTRUCTION,
    tools=[trigger_verification],
    sub_agents=[verifier_agent, analyzer_agent, roadmap_agent],
)


def get_root_agent() -> Agent:
    """Get the root counselor agent (the orchestrator).

    Returns:
        The configured root Agent with all sub-agents attached.
    """
    return counselor_agent
