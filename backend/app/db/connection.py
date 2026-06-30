"""Async MongoDB connection management using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


class MongoConnection:
    """Manages the MongoDB connection lifecycle."""

    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize the MongoDB connection."""
        cls._client = AsyncIOMotorClient(settings.mongodb_uri)
        cls._db = cls._client.get_default_database()

        # Verify connection
        await cls._client.admin.command("ping")
        print(f"✅ Connected to MongoDB: {cls._db.name}")

    @classmethod
    async def disconnect(cls) -> None:
        """Close the MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            print("🔌 MongoDB connection closed.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if cls._db is None:
            raise RuntimeError(
                "MongoDB not connected. Call MongoConnection.connect() first."
            )
        return cls._db

    @classmethod
    def get_collection(cls, name: str):
        """Get a collection by name."""
        return cls.get_db()[name]
