"""MongoDB repository layer for CRUD operations."""

from datetime import datetime, timezone
from typing import Any

from app.db.connection import MongoConnection


class UserProfileRepository:
    """Handles user profile persistence including verified skill scores."""

    COLLECTION = "user_profiles"

    @classmethod
    async def get_or_create_profile(cls, session_id: str) -> dict[str, Any]:
        """Retrieve an existing profile or create a new one."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        profile = await collection.find_one({"session_id": session_id})

        if profile is None:
            profile = {
                "session_id": session_id,
                "target_career": None,
                "claimed_skills": [],
                "verified_scores": [],
                "overall_score": None,
                "roadmap": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await collection.insert_one(profile)

        # Convert ObjectId to string for JSON serialization
        profile["_id"] = str(profile["_id"])
        return profile

    @classmethod
    async def update_target_career(
        cls, session_id: str, career: str, claimed_skills: list[str]
    ) -> None:
        """Update the student's target career and claimed skills."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        await collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "target_career": career,
                    "claimed_skills": claimed_skills,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

    @classmethod
    async def save_skill_scores(
        cls, session_id: str, scores: list[dict[str, Any]]
    ) -> None:
        """Upsert verified skill scores for a session."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        await collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "verified_scores": scores,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

    @classmethod
    async def save_overall_score(cls, session_id: str, score: float) -> None:
        """Save the computed overall verified skill score."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        await collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "overall_score": score,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

    @classmethod
    async def save_roadmap(
        cls, session_id: str, roadmap: list[dict[str, Any]]
    ) -> None:
        """Persist the generated career roadmap."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        await collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "roadmap": roadmap,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

    @classmethod
    async def get_profile_summary(cls, session_id: str) -> str:
        """Generate a text summary of a profile for injection into agent prompts."""
        profile = await cls.get_or_create_profile(session_id)

        if not profile.get("target_career"):
            return ""

        lines = [f"Returning student profile for session {session_id}:"]
        lines.append(f"- Target career: {profile['target_career']}")

        if profile.get("claimed_skills"):
            lines.append(
                f"- Claimed skills: {', '.join(profile['claimed_skills'])}"
            )

        if profile.get("verified_scores"):
            lines.append("- Previously verified scores:")
            for score in profile["verified_scores"]:
                lines.append(
                    f"  • {score['skill_name']}: {score['verified_score']}/{score['max_score']}"
                )

        if profile.get("overall_score") is not None:
            lines.append(f"- Overall verified score: {profile['overall_score']}%")

        return "\n".join(lines)


class RateLimitRepository:
    """Tracks API usage per IP for rate limiting."""

    COLLECTION = "rate_limits"

    @classmethod
    async def get_request_count(cls, ip_address: str, date_str: str) -> int:
        """Get the request count for an IP on a specific date."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        record = await collection.find_one(
            {"ip_address": ip_address, "date": date_str}
        )
        return record["count"] if record else 0

    @classmethod
    async def increment_request_count(cls, ip_address: str, date_str: str) -> int:
        """Increment and return the request count for an IP."""
        collection = MongoConnection.get_collection(cls.COLLECTION)
        result = await collection.find_one_and_update(
            {"ip_address": ip_address, "date": date_str},
            {
                "$inc": {"count": 1},
                "$setOnInsert": {
                    "ip_address": ip_address,
                    "date": date_str,
                    "created_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
            return_document=True,
        )
        return result["count"]
