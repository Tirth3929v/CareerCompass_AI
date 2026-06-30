"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field


# --- Request Models ---

class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message text")
    mode: str = Field(
        default="chat",
        description="Message mode: 'chat' for conversation, 'challenge_response' for skill verification answers",
    )


# --- Challenge Data Models ---

class ChallengeData(BaseModel):
    """Structure for a skill verification challenge."""

    type: str = Field(
        ..., description="Challenge type: 'code', 'math', or 'logic'"
    )
    question: str = Field(..., description="The challenge question text")
    skill_being_tested: str = Field(..., description="The skill this challenge verifies")
    difficulty: str = Field(default="intermediate", description="easy, intermediate, hard")
    options: list[str] | None = Field(
        default=None, description="Multiple choice options (for logic type)"
    )
    code_template: str | None = Field(
        default=None, description="Starter code template (for code type)"
    )
    expected_format: str | None = Field(
        default=None, description="Expected answer format hint"
    )
    time_limit_seconds: int = Field(
        default=300, description="Time limit for the challenge"
    )


# --- Score Models ---

class SkillScore(BaseModel):
    """Score for an individual skill after verification."""

    skill_name: str
    claimed_level: str = Field(
        default="beginner", description="Self-reported level: beginner, intermediate, advanced"
    )
    verified_score: float = Field(
        ..., ge=0, le=10, description="AI-verified score (0-10)"
    )
    max_score: float = Field(default=10.0)
    feedback: str = Field(default="", description="Detailed feedback on performance")


class AnalysisResult(BaseModel):
    """Full analysis output from the Analyzer agent."""

    target_career: str
    skill_scores: list[SkillScore]
    overall_score: float = Field(
        ..., ge=0, le=100, description="Overall verified skill score (0-100)"
    )
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    summary: str = Field(default="")


# --- Roadmap Models ---

class RoadmapResource(BaseModel):
    """A learning resource within a roadmap step."""

    title: str
    url: str
    type: str = Field(
        default="article", description="video, article, course, project, book"
    )
    is_free: bool = Field(default=True)


class RoadmapStep(BaseModel):
    """A single step in the career roadmap."""

    phase: int = Field(..., description="Phase number (1-based)")
    title: str
    description: str
    skills_covered: list[str] = Field(default_factory=list)
    resources: list[RoadmapResource] = Field(default_factory=list)
    duration_weeks: int = Field(default=2)
    milestone: str = Field(default="", description="What the student should achieve")


class Roadmap(BaseModel):
    """Complete career roadmap."""

    target_career: str
    total_duration_weeks: int
    phases: list[RoadmapStep]
    summary: str = Field(default="")


# --- Response Models ---

class ChatResponse(BaseModel):
    """Response sent back to the frontend."""

    message: str = Field(..., description="AI response text (markdown supported)")
    mode: str = Field(
        default="chat",
        description="Response mode: 'chat', 'verification', 'analysis', 'roadmap'",
    )
    challenge_data: ChallengeData | None = Field(
        default=None, description="Challenge data when mode is 'verification'"
    )
    skill_scores: list[SkillScore] | None = Field(
        default=None, description="Skill scores when mode is 'analysis'"
    )
    analysis: AnalysisResult | None = Field(
        default=None, description="Full analysis when mode is 'analysis'"
    )
    roadmap: Roadmap | None = Field(
        default=None, description="Career roadmap when mode is 'roadmap'"
    )


class SessionState(BaseModel):
    """Current state of a user's session."""

    session_id: str
    current_mode: str = Field(default="chat")
    target_career: str | None = None
    claimed_skills: list[str] = Field(default_factory=list)
    verified_scores: list[SkillScore] = Field(default_factory=list)
    overall_score: float | None = None
    roadmap: Roadmap | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    service: str = "careercompass-ai"
    version: str = "0.1.0"
