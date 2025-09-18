import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Callable
from motor.motor_asyncio import AsyncIOMotorDatabase
from .database import get_database

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: str, description: str, up_func: Callable, down_func: Callable = None):
        self.version = version
        self.description = description
        self.up_func = up_func
        self.down_func = down_func
        self.created_at = datetime.utcnow()


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self):
        self.migrations: List[Migration] = []
        self._register_migrations()
    
    def _register_migrations(self):
        """Register all available migrations"""
        # Migration 001: Initial schema setup
        self.migrations.append(Migration(
            version="001",
            description="Initial schema setup with collections and indexes",
            up_func=self._migration_001_up,
            down_func=self._migration_001_down
        ))
        
        # Migration 002: Add performance metrics to agents
        self.migrations.append(Migration(
            version="002", 
            description="Add performance metrics fields to agent collection",
            up_func=self._migration_002_up,
            down_func=self._migration_002_down
        ))
    
    async def run_migrations(self, target_version: str = None):
        """Run migrations up to target version (or all if None)"""
        db = await get_database()
        
        # Get current migration state
        current_version = await self._get_current_version(db)
        logger.info(f"Current migration version: {current_version}")
        
        # Determine which migrations to run
        migrations_to_run = []
        for migration in self.migrations:
            if current_version is None or migration.version > current_version:
                if target_version is None or migration.version <= target_version:
                    migrations_to_run.append(migration)
        
        if not migrations_to_run:
            logger.info("No migrations to run")
            return
        
        # Run migrations
        for migration in migrations_to_run:
            logger.info(f"Running migration {migration.version}: {migration.description}")
            try:
                await migration.up_func(db)
                await self._record_migration(db, migration)
                logger.info(f"Migration {migration.version} completed successfully")
            except Exception as e:
                logger.error(f"Migration {migration.version} failed: {e}")
                raise
    
    async def rollback_migration(self, target_version: str):
        """Rollback to a specific migration version"""
        db = await get_database()
        current_version = await self._get_current_version(db)
        
        if current_version is None or target_version >= current_version:
            logger.info("No rollback needed")
            return
        
        # Find migrations to rollback
        migrations_to_rollback = []
        for migration in reversed(self.migrations):
            if migration.version > target_version and migration.version <= current_version:
                migrations_to_rollback.append(migration)
        
        # Run rollbacks
        for migration in migrations_to_rollback:
            if migration.down_func:
                logger.info(f"Rolling back migration {migration.version}")
                try:
                    await migration.down_func(db)
                    await self._remove_migration_record(db, migration.version)
                    logger.info(f"Rollback of migration {migration.version} completed")
                except Exception as e:
                    logger.error(f"Rollback of migration {migration.version} failed: {e}")
                    raise
            else:
                logger.warning(f"No rollback function for migration {migration.version}")
    
    async def _get_current_version(self, db: AsyncIOMotorDatabase) -> str:
        """Get the current migration version"""
        migration_record = await db.migrations.find_one(
            {}, sort=[("version", -1)]
        )
        return migration_record["version"] if migration_record else None
    
    async def _record_migration(self, db: AsyncIOMotorDatabase, migration: Migration):
        """Record a completed migration"""
        await db.migrations.insert_one({
            "version": migration.version,
            "description": migration.description,
            "applied_at": datetime.utcnow()
        })
    
    async def _remove_migration_record(self, db: AsyncIOMotorDatabase, version: str):
        """Remove a migration record during rollback"""
        await db.migrations.delete_one({"version": version})
    
    # Migration functions
    async def _migration_001_up(self, db: AsyncIOMotorDatabase):
        """Initial schema setup"""
        # Create collections if they don't exist
        collections = ["workflows", "agents", "debate_threads", "resources", "users", "migrations"]
        existing_collections = await db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
    
    async def _migration_001_down(self, db: AsyncIOMotorDatabase):
        """Rollback initial schema setup"""
        # This is destructive - only use in development
        collections = ["workflows", "agents", "debate_threads", "resources", "users"]
        for collection_name in collections:
            await db.drop_collection(collection_name)
            logger.info(f"Dropped collection: {collection_name}")
    
    async def _migration_002_up(self, db: AsyncIOMotorDatabase):
        """Add performance metrics to agents"""
        # Update existing agents to have performance_metrics field
        await db.agents.update_many(
            {"performance_metrics": {"$exists": False}},
            {"$set": {"performance_metrics": {}}}
        )
        logger.info("Added performance_metrics field to existing agents")
    
    async def _migration_002_down(self, db: AsyncIOMotorDatabase):
        """Remove performance metrics from agents"""
        await db.agents.update_many(
            {},
            {"$unset": {"performance_metrics": ""}}
        )
        logger.info("Removed performance_metrics field from agents")


# Global migration manager instance
migration_manager = MigrationManager()


async def run_migrations(target_version: str = None):
    """Run database migrations"""
    await migration_manager.run_migrations(target_version)


async def rollback_migrations(target_version: str):
    """Rollback database migrations"""
    await migration_manager.rollback_migration(target_version)