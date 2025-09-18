#!/usr/bin/env python3
"""
Database initialization script for Rendezvous system.
This script sets up the database, runs migrations, and creates initial data.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import List

from .database import connect_databases, disconnect_databases
from .migrations import run_migrations
from .repositories import AgentRepository, UserRepository
from ..models import Agent, AgentCapability, AgentStatus, User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_default_agents() -> None:
    """Create default system agents"""
    agent_repo = AgentRepository()
    
    # Default agent configurations
    default_agents = [
        {
            "name": "search-agent",
            "version": "1.0.0",
            "endpoint": "http://localhost:8001",
            "capabilities": [
                AgentCapability(
                    name="web_search",
                    description="Search the web for information",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "max_results": {"type": "integer", "default": 10}
                        },
                        "required": ["query"]
                    },
                    output_schema={
                        "type": "object", 
                        "properties": {
                            "results": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "url": {"type": "string"},
                                        "snippet": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    debate_enabled=False
                ),
                AgentCapability(
                    name="semantic_search",
                    description="Perform semantic search on resources",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "resource_types": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["query"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "resources": {"type": "array"}
                        }
                    },
                    debate_enabled=False
                )
            ]
        },
        {
            "name": "summarize-agent", 
            "version": "1.0.0",
            "endpoint": "http://localhost:8002",
            "capabilities": [
                AgentCapability(
                    name="text_summarization",
                    description="Summarize text content",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "max_length": {"type": "integer", "default": 200}
                        },
                        "required": ["text"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "key_points": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    debate_enabled=True
                )
            ]
        },
        {
            "name": "debate-agent",
            "version": "1.0.0", 
            "endpoint": "http://localhost:8003",
            "capabilities": [
                AgentCapability(
                    name="argument_analysis",
                    description="Analyze arguments and generate counter-arguments",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "argument": {"type": "string"},
                            "context": {"type": "string"}
                        },
                        "required": ["argument"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "analysis": {"type": "string"},
                            "counter_arguments": {"type": "array", "items": {"type": "string"}},
                            "strength_score": {"type": "number"}
                        }
                    },
                    debate_enabled=True
                )
            ]
        },
        {
            "name": "draft-agent",
            "version": "1.0.0",
            "endpoint": "http://localhost:8004", 
            "capabilities": [
                AgentCapability(
                    name="content_creation",
                    description="Create and format content",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_type": {"type": "string"},
                            "requirements": {"type": "object"},
                            "sources": {"type": "array"}
                        },
                        "required": ["content_type"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "metadata": {"type": "object"}
                        }
                    },
                    debate_enabled=True
                )
            ]
        },
        {
            "name": "review-agent",
            "version": "1.0.0",
            "endpoint": "http://localhost:8005",
            "capabilities": [
                AgentCapability(
                    name="quality_assessment",
                    description="Review and assess content quality",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "criteria": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["content"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "score": {"type": "number"},
                            "feedback": {"type": "string"},
                            "suggestions": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    debate_enabled=True
                )
            ]
        }
    ]
    
    # Create agents if they don't exist
    for agent_config in default_agents:
        existing_agent = await agent_repo.get_by_name(agent_config["name"])
        if not existing_agent:
            agent = Agent(
                name=agent_config["name"],
                version=agent_config["version"],
                endpoint=agent_config["endpoint"],
                capabilities=agent_config["capabilities"],
                status=AgentStatus.OFFLINE
            )
            agent_id = await agent_repo.create(agent)
            logger.info(f"Created default agent: {agent_config['name']} (ID: {agent_id})")
        else:
            logger.info(f"Agent {agent_config['name']} already exists")


async def create_admin_user() -> None:
    """Create default admin user if it doesn't exist"""
    user_repo = UserRepository()
    
    admin_email = os.getenv("ADMIN_EMAIL", "admin@rendezvous.local")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # Should be hashed in production
    
    existing_user = await user_repo.get_by_email(admin_email)
    if not existing_user:
        admin_user = User(
            email=admin_email,
            username=admin_username,
            hashed_password=admin_password,  # In production, this should be properly hashed
            is_active=True,
            preferences={
                "theme": "dark",
                "notifications": True,
                "auto_save": True
            }
        )
        user_id = await user_repo.create(admin_user)
        logger.info(f"Created admin user: {admin_email} (ID: {user_id})")
    else:
        logger.info(f"Admin user {admin_email} already exists")


async def initialize_database():
    """Initialize the database with schema and default data"""
    try:
        logger.info("Starting database initialization...")
        
        # Connect to databases
        await connect_databases()
        logger.info("Connected to databases")
        
        # Run migrations
        logger.info("Running database migrations...")
        await run_migrations()
        logger.info("Migrations completed")
        
        # Create default data
        logger.info("Creating default agents...")
        await create_default_agents()
        
        logger.info("Creating admin user...")
        await create_admin_user()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await disconnect_databases()


if __name__ == "__main__":
    asyncio.run(initialize_database())