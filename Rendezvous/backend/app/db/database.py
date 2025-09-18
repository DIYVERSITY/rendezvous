import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as redis
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB and Redis connections"""
    
    def __init__(self):
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect_mongodb(self, connection_string: str, database_name: str):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = AsyncIOMotorClient(connection_string)
            self.database = self.mongodb_client[database_name]
            
            # Test the connection
            await self.mongodb_client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def connect_redis(self, redis_url: str):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test the connection
            await self.redis_client.ping()
            logger.info("Connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from all databases"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("Disconnected from MongoDB")
            
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        if not self.database:
            return
            
        try:
            # Workflow indexes
            workflow_indexes = [
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("status", ASCENDING)]),
            ]
            await self.database.workflows.create_indexes(workflow_indexes)
            
            # Agent indexes
            agent_indexes = [
                IndexModel([("name", ASCENDING)], unique=True),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("last_heartbeat", DESCENDING)]),
                IndexModel([("capabilities.name", ASCENDING)]),
            ]
            await self.database.agents.create_indexes(agent_indexes)
            
            # Debate thread indexes
            debate_indexes = [
                IndexModel([("workflow_id", ASCENDING)]),
                IndexModel([("step_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("participants", ASCENDING)]),
            ]
            await self.database.debate_threads.create_indexes(debate_indexes)
            
            # Resource indexes
            resource_indexes = [
                IndexModel([("workflow_id", ASCENDING)]),
                IndexModel([("type", ASCENDING)]),
                IndexModel([("tags", ASCENDING)]),
                IndexModel([("created_by", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ]
            await self.database.resources.create_indexes(resource_indexes)
            
            # User indexes
            user_indexes = [
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("username", ASCENDING)], unique=True),
                IndexModel([("is_active", ASCENDING)]),
            ]
            await self.database.users.create_indexes(user_indexes)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Get the MongoDB database instance"""
    if not db_manager.database:
        raise RuntimeError("Database not connected. Call connect_databases() first.")
    return db_manager.database


async def get_redis() -> redis.Redis:
    """Get the Redis client instance"""
    if not db_manager.redis_client:
        raise RuntimeError("Redis not connected. Call connect_databases() first.")
    return db_manager.redis_client


async def connect_databases():
    """Connect to all databases using environment variables"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "rendezvous")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    await db_manager.connect_mongodb(mongodb_url, database_name)
    await db_manager.connect_redis(redis_url)


async def disconnect_databases():
    """Disconnect from all databases"""
    await db_manager.disconnect()