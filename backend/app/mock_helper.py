"""Mock data generators for running CareerCompass AI in offline Mock Mode."""

from typing import Any
from app.models.schemas import (
    ChallengeData,
    SkillScore,
    AnalysisResult,
    Roadmap,
    RoadmapStep,
    RoadmapResource,
    ChatRequest,
    ChatResponse,
)

def get_mock_challenge(career: str, index: int) -> ChallengeData:
    """Generate a mock ChallengeData object based on career and index (0-2)."""
    # Normalize career names
    career_lower = career.lower()
    
    if "ai" in career_lower or "machine" in career_lower or "ml" in career_lower:
        challenges = [
            ChallengeData(
                type="code",
                question="Write a Python function to compute the moving average of a list of numbers with a given window size.",
                skill_being_tested="Python",
                difficulty="intermediate",
                code_template="def moving_average(numbers: list[float], window: int) -> list[float]:\n    # Write your code here\n    pass",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="math",
                question="Calculate the dot product of vectors A = [2, 3, -1] and B = [4, -2, 5].",
                skill_being_tested="Mathematics (Linear Algebra)",
                difficulty="intermediate",
                expected_format="numeric",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="logic",
                question="Which of the following activation functions can cause the 'dying ReLU' problem where neurons output zero and stop updating?",
                skill_being_tested="Machine Learning Concepts",
                difficulty="intermediate",
                options=["A) Sigmoid", "B) Tanh", "C) ReLU", "D) Leaky ReLU"],
                time_limit_seconds=180
            )
        ]
    elif "stack" in career_lower or "dev" in career_lower or "web" in career_lower:
        challenges = [
            ChallengeData(
                type="code",
                question="Write a JavaScript function to check if a string is a palindrome (ignores spaces, punctuation, and capitalization).",
                skill_being_tested="JavaScript",
                difficulty="intermediate",
                code_template="function isPalindrome(str) {\n  // Write your code here\n}",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="code",
                question="Write an SQL query to find the second highest salary from the Employee table. If there is no second highest salary, return NULL.",
                skill_being_tested="Databases/SQL",
                difficulty="intermediate",
                code_template="SELECT MAX(Salary) FROM Employee WHERE Salary < (SELECT MAX(Salary) FROM Employee);",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="logic",
                question="Which HTTP method should be used to update an existing resource partially, rather than replacing the entire resource?",
                skill_being_tested="REST APIs",
                difficulty="intermediate",
                options=["A) POST", "B) PUT", "C) PATCH", "D) DELETE"],
                time_limit_seconds=180
            )
        ]
    elif "data" in career_lower:
        challenges = [
            ChallengeData(
                type="code",
                question="Write a Python function using pandas to filter a DataFrame for rows where the column 'age' is greater than 30.",
                skill_being_tested="Python",
                difficulty="intermediate",
                code_template="import pandas as pd\n\ndef filter_data(df: pd.DataFrame) -> pd.DataFrame:\n    # Write your code here\n    pass",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="math",
                question="If the probability of an event happening is 0.3, what is the probability of it happening exactly twice in three independent trials?",
                skill_being_tested="Statistics",
                difficulty="intermediate",
                expected_format="numeric",
                time_limit_seconds=300
            ),
            ChallengeData(
                type="code",
                question="Write an SQL query to count the number of users grouped by their country, sorted in descending order of count.",
                skill_being_tested="SQL",
                difficulty="intermediate",
                code_template="SELECT country, COUNT(*) FROM users GROUP BY ...",
                time_limit_seconds=300
            )
        ]
    else: # Cloud / DevOps / default
        challenges = [
            ChallengeData(
                type="logic",
                question="Which AWS service is designed to deliver low-latency web content to global users using a network of edge locations?",
                skill_being_tested="AWS",
                difficulty="intermediate",
                options=["A) Amazon S3", "B) Amazon Route 53", "C) Amazon CloudFront", "D) AWS Direct Connect"],
                time_limit_seconds=180
            ),
            ChallengeData(
                type="logic",
                question="Which port is used by default for secure SSH shell communications?",
                skill_being_tested="Networking",
                difficulty="intermediate",
                options=["A) Port 80", "B) Port 443", "C) Port 22", "D) Port 8080"],
                time_limit_seconds=180
            ),
            ChallengeData(
                type="logic",
                question="Which command is used to change file permissions in Linux/Unix operating systems?",
                skill_being_tested="Linux",
                difficulty="intermediate",
                options=["A) chown", "B) chmod", "C) chgrp", "D) perm"],
                time_limit_seconds=180
            )
        ]
        
    return challenges[min(index, len(challenges) - 1)]

def get_mock_analysis(career: str, scores: list[dict[str, Any]]) -> AnalysisResult:
    """Generate a mock AnalysisResult based on career and scores."""
    skill_scores = [
        SkillScore(
            skill_name=s["skill_name"],
            claimed_level=s.get("claimed_level", "intermediate"),
            verified_score=float(s["verified_score"]),
            max_score=10.0,
            feedback=s.get("feedback", "Excellent performance.")
        )
        for s in scores
    ]
    
    avg_score = sum(s.verified_score for s in skill_scores) / len(skill_scores) if skill_scores else 8.0
    overall = round(avg_score * 10.0)
    
    return AnalysisResult(
        target_career=career,
        skill_scores=skill_scores,
        overall_score=float(overall),
        strengths=[s.skill_name for s in skill_scores if s.verified_score >= 8],
        gaps=[s.skill_name for s in skill_scores if s.verified_score < 8] or ["Advanced System Architecture"],
        summary=(
            f"You demonstrate solid foundational knowledge required for a {career} role. "
            "Your understanding of basic concepts is strong, but focusing on hands-on practical application "
            "will help bridge the remaining gaps to make you job-ready."
        )
    )

def get_mock_roadmap(career: str) -> Roadmap:
    """Generate a mock Roadmap for a career path."""
    return Roadmap(
        target_career=career,
        total_duration_weeks=20,
        summary=f"This 20-week learning roadmap is designed to guide your transition into a successful {career} role.",
        phases=[
            RoadmapStep(
                phase=1,
                title="Foundation & Fundamentals",
                description="Strengthen your core programming, syntax, and fundamental logic required for the path.",
                skills_covered=["Basic Scripting", "Logic Gate Fundamentals"],
                resources=[
                    RoadmapResource(title="Introduction to Programming Course", url="https://www.freecodecamp.org", type="course", is_free=True),
                    RoadmapResource(title="Logic Fundamentals Guide", url="https://www.coursera.org", type="article", is_free=True)
                ],
                duration_weeks=4,
                milestone="Build a basic application command-line tool."
            ),
            RoadmapStep(
                phase=2,
                title="Core Technology Stack",
                description="Deep dive into the primary framework, cloud platform, or model paradigms essential to this career.",
                skills_covered=["Advanced Frameworks", "API Design"],
                resources=[
                    RoadmapResource(title="Core Tech Crash Course", url="https://www.youtube.com", type="video", is_free=True),
                    RoadmapResource(title="Official Technical Documentation", url="https://docs.microsoft.com", type="article", is_free=True)
                ],
                duration_weeks=6,
                milestone="Complete a medium-scale backend API integration."
            ),
            RoadmapStep(
                phase=3,
                title="Applied Engineering & Databases",
                description="Learn to scale your application using production-ready systems, database indexing, and orchestration.",
                skills_covered=["Databases", "Containerization"],
                resources=[
                    RoadmapResource(title="Docker and SQL Mastery Course", url="https://www.freecodecamp.org", type="course", is_free=True)
                ],
                duration_weeks=6,
                milestone="Deploy a containerized application to staging/production."
            ),
            RoadmapStep(
                phase=4,
                title="Career Readiness & Projects",
                description="Polish your resume, build a stellar Capstone project, and practice interview questions.",
                skills_covered=["System Design", "Behavioral Prep"],
                resources=[
                    RoadmapResource(title="Tech Interview Guide", url="https://github.com", type="project", is_free=True)
                ],
                duration_weeks=4,
                milestone="Share your portfolio site with 3 peers and a mentor."
            )
        ]
    )


# A simple global dictionary to keep track of mock session states
_mock_sessions: dict[str, dict[str, Any]] = {}

def generate_mock_response(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id
    message = request.message.strip().lower()
    
    if session_id not in _mock_sessions:
        _mock_sessions[session_id] = {
            "step": 0,
            "career": "AI Engineer",
            "skills": ["Python", "Mathematics", "Machine Learning Concepts"],
            "scores": []
        }
        
    state = _mock_sessions[session_id]
    
    # Reset command or start over
    if "reset" in message or "restart" in message:
        state["step"] = 0
        state["career"] = "AI Engineer"
        state["scores"] = []
        return ChatResponse(
            message="Let's start over! What career path are you interested in?",
            mode="chat"
        )
        
    step = state["step"]
    
    if step == 0:
        # User tells us their career goal
        # e.g. "I want to become an AI Engineer"
        career = "AI Engineer"
        if "web" in message or "developer" in message or "fullstack" in message:
            career = "Fullstack Developer"
            state["skills"] = ["JavaScript", "SQL", "REST APIs"]
        elif "data" in message:
            career = "Data Scientist"
            state["skills"] = ["Python", "Statistics", "SQL"]
            
        state["career"] = career
        state["step"] = 1
        return ChatResponse(
            message=f"A career as an {career} is an excellent choice! To help you verify your skills, I'll ask you a few questions. Are you ready to start with the first challenge?",
            mode="chat"
        )
        
    elif step == 1:
        # User says "yes" to starting the first challenge
        state["step"] = 2
        challenge = get_mock_challenge(state["career"], 0)
        return ChatResponse(
            message=f"Great! Let's start with your first challenge: {challenge.skill_being_tested}.",
            mode="verification",
            challenge_data=challenge
        )
        
    elif step == 2:
        # User submitted answer to challenge 0
        state["scores"].append({
            "skill_name": state["skills"][0],
            "verified_score": 8.5,
            "feedback": "Great Python implementation! Clean, efficient, and well-structured."
        })
        state["step"] = 3
        challenge = get_mock_challenge(state["career"], 1)
        return ChatResponse(
            message=f"Nice job on the Python challenge! Here is your next challenge: {challenge.skill_being_tested}.",
            mode="verification",
            challenge_data=challenge
        )
        
    elif step == 3:
        # User submitted answer to challenge 1
        state["scores"].append({
            "skill_name": state["skills"][1],
            "verified_score": 9.0,
            "feedback": "Excellent performance on mathematics/SQL challenge."
        })
        state["step"] = 4
        challenge = get_mock_challenge(state["career"], 2)
        return ChatResponse(
            message=f"Perfect. Let's do the final challenge: {challenge.skill_being_tested}.",
            mode="verification",
            challenge_data=challenge
        )
        
    elif step == 4:
        # User submitted answer to challenge 2
        state["scores"].append({
            "skill_name": state["skills"][2],
            "verified_score": 7.5,
            "feedback": "Solid conceptual understanding, but could improve on details."
        })
        state["step"] = 5
        analysis = get_mock_analysis(state["career"], state["scores"])
        
        # Build SkillScore objects for ChatResponse
        from app.models.schemas import SkillScore
        skill_scores_obj = [
            SkillScore(
                skill_name=s["skill_name"],
                verified_score=s["verified_score"],
                feedback=s["feedback"]
            )
            for s in state["scores"]
        ]
        
        return ChatResponse(
            message=f"Verification complete! Here is your skill assessment analysis for {state['career']}.",
            mode="analysis",
            skill_scores=skill_scores_obj,
            analysis=analysis
        )
        
    elif step == 5:
        # User asks for roadmap
        state["step"] = 6
        roadmap = get_mock_roadmap(state["career"])
        return ChatResponse(
            message=f"Based on your skill assessment, here is your personalized {state['career']} roadmap:",
            mode="roadmap",
            roadmap=roadmap
        )
        
    else:
        # Restart
        state["step"] = 0
        state["scores"] = []
        return ChatResponse(
            message="We have completed the mock flow. Type 'restart' or 'reset' to start over!",
            mode="chat"
        )
