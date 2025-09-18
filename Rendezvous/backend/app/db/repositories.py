from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis
from bson import ObjectId

from ..models import (
    Workflow, WorkflowStep, WorkflowStatus, StepStatus,
    Agent, AgentStatus, 
    DebateThread, DebateStatus, CoralMessage,
    Resource, User
)
from .database import get_database, get_redis


class BaseRepository:
    """Base repository with common functionality"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    async def get_collection(self):
        """Get the MongoDB collection"""
        db = await get_database()
        return db[self.collection_name]
    
    async def get_redis(self):
        """Get Redis client"""
        return await get_redis()


class WorkflowRepository(BaseRepository):
    """Repository for workflow operations"""
    
    def __init__(self):
        super().__init__("workflows")
    
    async def create(self, workflow: Workflow) -> str:
        """Create a new workflow"""
        collection = await self.get_collection()
        workflow_dict = workflow.dict()
        result = await collection.insert_one(workflow_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        collection = await self.get_collection()
        workflow_data = await collection.find_one({"_id": ObjectId(workflow_id)})
        if workflow_data:
            workflow_data["id"] = str(workflow_data["_id"])
            del workflow_data["_id"]
            return Workflow(**workflow_data)
        return None
    
    async def get_by_user_id(self, user_id: str, limit: int = 50) -> List[Workflow]:
        """Get workflows by user ID"""
        collection = await self.get_collection()
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        workflows = []
        async for workflow_data in cursor:
            workflow_data["id"] = str(workflow_data["_id"])
            del workflow_data["_id"]
            workflows.append(Workflow(**workflow_data))
        return workflows
    
    async def update(self, workflow: Workflow) -> bool:
        """Update an existing workflow"""
        collection = await self.get_collection()
        workflow.updated_at = datetime.utcnow()
        workflow_dict = workflow.dict()
        workflow_dict["_id"] = ObjectId(workflow.id)
        del workflow_dict["id"]
        
        result = await collection.replace_one(
            {"_id": ObjectId(workflow.id)}, 
            workflow_dict
        )
        return result.modified_count > 0
    
    async def delete(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(workflow_id)})
        return result.deleted_count > 0
    
    async def get_active_workflows(self) -> List[Workflow]:
        """Get all active workflows"""
        collection = await self.get_collection()
        cursor = collection.find({
            "status": {"$in": [WorkflowStatus.EXECUTING, WorkflowStatus.PAUSED]}
        })
        workflows = []
        async for workflow_data in cursor:
            workflow_data["id"] = str(workflow_data["_id"])
            del workflow_data["_id"]
            workflows.append(Workflow(**workflow_data))
        return workflows


class AgentRepository(BaseRepository):
    """Repository for agent operations"""
    
    def __init__(self):
        super().__init__("agents")
    
    async def create(self, agent: Agent) -> str:
        """Create a new agent"""
        collection = await self.get_collection()
        agent_dict = agent.dict()
        result = await collection.insert_one(agent_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        collection = await self.get_collection()
        agent_data = await collection.find_one({"_id": ObjectId(agent_id)})
        if agent_data:
            agent_data["id"] = str(agent_data["_id"])
            del agent_data["_id"]
            return Agent(**agent_data)
        return None
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        collection = await self.get_collection()
        agent_data = await collection.find_one({"name": name})
        if agent_data:
            agent_data["id"] = str(agent_data["_id"])
            del agent_data["_id"]
            return Agent(**agent_data)
        return None
    
    async def get_all(self) -> List[Agent]:
        """Get all agents"""
        collection = await self.get_collection()
        cursor = collection.find({})
        agents = []
        async for agent_data in cursor:
            agent_data["id"] = str(agent_data["_id"])
            del agent_data["_id"]
            agents.append(Agent(**agent_data))
        return agents
    
    async def get_by_capability(self, capability_name: str) -> List[Agent]:
        """Get agents with specific capability"""
        collection = await self.get_collection()
        cursor = collection.find({"capabilities.name": capability_name})
        agents = []
        async for agent_data in cursor:
            agent_data["id"] = str(agent_data["_id"])
            del agent_data["_id"]
            agents.append(Agent(**agent_data))
        return agents
    
    async def get_healthy_agents(self, timeout_seconds: int = 300) -> List[Agent]:
        """Get all healthy agents"""
        collection = await self.get_collection()
        cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        cursor = collection.find({
            "status": {"$ne": AgentStatus.OFFLINE},
            "last_heartbeat": {"$gte": cutoff_time}
        })
        agents = []
        async for agent_data in cursor:
            agent_data["id"] = str(agent_data["_id"])
            del agent_data["_id"]
            agents.append(Agent(**agent_data))
        return agents
    
    async def update(self, agent: Agent) -> bool:
        """Update an existing agent"""
        collection = await self.get_collection()
        agent.updated_at = datetime.utcnow()
        agent_dict = agent.dict()
        agent_dict["_id"] = ObjectId(agent.id)
        del agent_dict["id"]
        
        result = await collection.replace_one(
            {"_id": ObjectId(agent.id)}, 
            agent_dict
        )
        return result.modified_count > 0
    
    async def update_heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        collection = await self.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "last_heartbeat": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def delete(self, agent_id: str) -> bool:
        """Delete an agent"""
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(agent_id)})
        return result.deleted_count > 0


class DebateRepository(BaseRepository):
    """Repository for debate thread operations"""
    
    def __init__(self):
        super().__init__("debate_threads")
    
    async def create(self, debate: DebateThread) -> str:
        """Create a new debate thread"""
        collection = await self.get_collection()
        debate_dict = debate.dict()
        result = await collection.insert_one(debate_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, debate_id: str) -> Optional[DebateThread]:
        """Get debate thread by ID"""
        collection = await self.get_collection()
        debate_data = await collection.find_one({"_id": ObjectId(debate_id)})
        if debate_data:
            debate_data["id"] = str(debate_data["_id"])
            del debate_data["_id"]
            return DebateThread(**debate_data)
        return None
    
    async def get_by_workflow_id(self, workflow_id: str) -> List[DebateThread]:
        """Get debate threads by workflow ID"""
        collection = await self.get_collection()
        cursor = collection.find({"workflow_id": workflow_id})
        debates = []
        async for debate_data in cursor:
            debate_data["id"] = str(debate_data["_id"])
            del debate_data["_id"]
            debates.append(DebateThread(**debate_data))
        return debates
    
    async def get_by_step_id(self, step_id: str) -> Optional[DebateThread]:
        """Get debate thread by step ID"""
        collection = await self.get_collection()
        debate_data = await collection.find_one({"step_id": step_id})
        if debate_data:
            debate_data["id"] = str(debate_data["_id"])
            del debate_data["_id"]
            return DebateThread(**debate_data)
        return None
    
    async def update(self, debate: DebateThread) -> bool:
        """Update an existing debate thread"""
        collection = await self.get_collection()
        debate.updated_at = datetime.utcnow()
        debate_dict = debate.dict()
        debate_dict["_id"] = ObjectId(debate.id)
        del debate_dict["id"]
        
        result = await collection.replace_one(
            {"_id": ObjectId(debate.id)}, 
            debate_dict
        )
        return result.modified_count > 0
    
    async def get_active_debates(self) -> List[DebateThread]:
        """Get all active debate threads"""
        collection = await self.get_collection()
        cursor = collection.find({"status": DebateStatus.ACTIVE})
        debates = []
        async for debate_data in cursor:
            debate_data["id"] = str(debate_data["_id"])
            del debate_data["_id"]
            debates.append(DebateThread(**debate_data))
        return debates


class ResourceRepository(BaseRepository):
    """Repository for resource operations"""
    
    def __init__(self):
        super().__init__("resources")
    
    async def create(self, resource: Resource) -> str:
        """Create a new resource"""
        collection = await self.get_collection()
        resource_dict = resource.dict()
        result = await collection.insert_one(resource_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID"""
        collection = await self.get_collection()
        resource_data = await collection.find_one({"_id": ObjectId(resource_id)})
        if resource_data:
            resource_data["id"] = str(resource_data["_id"])
            del resource_data["_id"]
            return Resource(**resource_data)
        return None
    
    async def get_by_workflow_id(self, workflow_id: str) -> List[Resource]:
        """Get resources by workflow ID"""
        collection = await self.get_collection()
        cursor = collection.find({"workflow_id": workflow_id})
        resources = []
        async for resource_data in cursor:
            resource_data["id"] = str(resource_data["_id"])
            del resource_data["_id"]
            resources.append(Resource(**resource_data))
        return resources
    
    async def get_by_tags(self, tags: List[str]) -> List[Resource]:
        """Get resources by tags"""
        collection = await self.get_collection()
        cursor = collection.find({"tags": {"$in": tags}})
        resources = []
        async for resource_data in cursor:
            resource_data["id"] = str(resource_data["_id"])
            del resource_data["_id"]
            resources.append(Resource(**resource_data))
        return resources
    
    async def search_by_type(self, resource_type: str, limit: int = 50) -> List[Resource]:
        """Search resources by type"""
        collection = await self.get_collection()
        cursor = collection.find({"type": resource_type}).limit(limit)
        resources = []
        async for resource_data in cursor:
            resource_data["id"] = str(resource_data["_id"])
            del resource_data["_id"]
            resources.append(Resource(**resource_data))
        return resources
    
    async def update(self, resource: Resource) -> bool:
        """Update an existing resource"""
        collection = await self.get_collection()
        resource.updated_at = datetime.utcnow()
        resource_dict = resource.dict()
        resource_dict["_id"] = ObjectId(resource.id)
        del resource_dict["id"]
        
        result = await collection.replace_one(
            {"_id": ObjectId(resource.id)}, 
            resource_dict
        )
        return result.modified_count > 0
    
    async def delete(self, resource_id: str) -> bool:
        """Delete a resource"""
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(resource_id)})
        return result.deleted_count > 0


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self):
        super().__init__("users")
    
    async def create(self, user: User) -> str:
        """Create a new user"""
        collection = await self.get_collection()
        user_dict = user.dict()
        result = await collection.insert_one(user_dict)
        return str(result.inserted_id)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        collection = await self.get_collection()
        user_data = await collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            return User(**user_data)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        collection = await self.get_collection()
        user_data = await collection.find_one({"email": email})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            return User(**user_data)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        collection = await self.get_collection()
        user_data = await collection.find_one({"username": username})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            return User(**user_data)
        return None
    
    async def update(self, user: User) -> bool:
        """Update an existing user"""
        collection = await self.get_collection()
        user.updated_at = datetime.utcnow()
        user_dict = user.dict()
        user_dict["_id"] = ObjectId(user.id)
        del user_dict["id"]
        
        result = await collection.replace_one(
            {"_id": ObjectId(user.id)}, 
            user_dict
        )
        return result.modified_count > 0
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0