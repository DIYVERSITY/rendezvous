import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.database import DatabaseManager, connect_databases, disconnect_databases
from app.db.repositories import (
    WorkflowRepository, AgentRepository, DebateRepository, 
    ResourceRepository, UserRepository
)
from app.models import (
    Workflow, WorkflowStatus, Agent, AgentStatus, AgentCapability,
    DebateThread, DebateStatus, CoralMessage, Resource, User
)


class TestDatabaseManager:
    """Test database manager functionality"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a database manager instance"""
        return DatabaseManager()
    
    @patch('app.db.database.AsyncIOMotorClient')
    async def test_connect_mongodb(self, mock_client, db_manager):
        """Test MongoDB connection"""
        mock_client_instance = AsyncMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.admin.command = AsyncMock()
        
        await db_manager.connect_mongodb("mongodb://localhost:27017", "test_db")
        
        assert db_manager.mongodb_client is not None
        assert db_manager.database is not None
        mock_client_instance.admin.command.assert_called_once_with('ping')
    
    @patch('app.db.database.redis.from_url')
    async def test_connect_redis(self, mock_redis, db_manager):
        """Test Redis connection"""
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.ping = AsyncMock()
        
        await db_manager.connect_redis("redis://localhost:6379")
        
        assert db_manager.redis_client is not None
        mock_redis_instance.ping.assert_called_once()
    
    async def test_disconnect(self, db_manager):
        """Test database disconnection"""
        # Mock connections
        db_manager.mongodb_client = MagicMock()
        db_manager.redis_client = AsyncMock()
        
        await db_manager.disconnect()
        
        db_manager.mongodb_client.close.assert_called_once()
        db_manager.redis_client.close.assert_called_once()


class TestWorkflowRepository:
    """Test workflow repository operations"""
    
    @pytest.fixture
    def workflow_repo(self):
        """Create workflow repository instance"""
        return WorkflowRepository()
    
    @pytest.fixture
    def sample_workflow(self):
        """Create sample workflow for testing"""
        return Workflow(
            user_id="user123",
            prompt="Test workflow prompt",
            status=WorkflowStatus.PLANNING
        )
    
    @patch('app.db.repositories.get_database')
    async def test_create_workflow(self, mock_get_db, workflow_repo, sample_workflow):
        """Test workflow creation"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.inserted_id = "workflow_id_123"
        mock_collection.insert_one.return_value = mock_result
        
        result = await workflow_repo.create(sample_workflow)
        
        assert result == "workflow_id_123"
        mock_collection.insert_one.assert_called_once()
    
    @patch('app.db.repositories.get_database')
    async def test_get_workflow_by_id(self, mock_get_db, workflow_repo):
        """Test getting workflow by ID"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        workflow_data = {
            "_id": "workflow_id_123",
            "user_id": "user123",
            "prompt": "Test prompt",
            "status": "planning",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "agents_assigned": [],
            "current_step": 0,
            "total_steps": 0,
            "mind_map_data": {},
            "steps": []
        }
        mock_collection.find_one.return_value = workflow_data
        
        result = await workflow_repo.get_by_id("workflow_id_123")
        
        assert result is not None
        assert result.id == "workflow_id_123"
        assert result.user_id == "user123"
        assert result.prompt == "Test prompt"
    
    @patch('app.db.repositories.get_database')
    async def test_get_workflows_by_user_id(self, mock_get_db, workflow_repo):
        """Test getting workflows by user ID"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        workflow_data = {
            "_id": "workflow_id_123",
            "user_id": "user123",
            "prompt": "Test prompt",
            "status": "planning",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "agents_assigned": [],
            "current_step": 0,
            "total_steps": 0,
            "mind_map_data": {},
            "steps": []
        }
        
        # Mock async iteration
        mock_cursor.__aiter__.return_value = [workflow_data]
        
        result = await workflow_repo.get_by_user_id("user123")
        
        assert len(result) == 1
        assert result[0].user_id == "user123"


class TestAgentRepository:
    """Test agent repository operations"""
    
    @pytest.fixture
    def agent_repo(self):
        """Create agent repository instance"""
        return AgentRepository()
    
    @pytest.fixture
    def sample_agent(self):
        """Create sample agent for testing"""
        capability = AgentCapability(
            name="test_capability",
            description="Test capability",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        return Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000",
            capabilities=[capability],
            status=AgentStatus.ONLINE
        )
    
    @patch('app.db.repositories.get_database')
    async def test_create_agent(self, mock_get_db, agent_repo, sample_agent):
        """Test agent creation"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.inserted_id = "agent_id_123"
        mock_collection.insert_one.return_value = mock_result
        
        result = await agent_repo.create(sample_agent)
        
        assert result == "agent_id_123"
        mock_collection.insert_one.assert_called_once()
    
    @patch('app.db.repositories.get_database')
    async def test_get_agent_by_name(self, mock_get_db, agent_repo):
        """Test getting agent by name"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        agent_data = {
            "_id": "agent_id_123",
            "name": "test-agent",
            "version": "1.0.0",
            "endpoint": "http://localhost:8000",
            "capabilities": [],
            "status": "online",
            "last_heartbeat": datetime.utcnow(),
            "performance_metrics": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mock_collection.find_one.return_value = agent_data
        
        result = await agent_repo.get_by_name("test-agent")
        
        assert result is not None
        assert result.name == "test-agent"
        assert result.id == "agent_id_123"
    
    @patch('app.db.repositories.get_database')
    async def test_get_healthy_agents(self, mock_get_db, agent_repo):
        """Test getting healthy agents"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_collection.find.return_value = mock_cursor
        
        agent_data = {
            "_id": "agent_id_123",
            "name": "test-agent",
            "version": "1.0.0",
            "endpoint": "http://localhost:8000",
            "capabilities": [],
            "status": "online",
            "last_heartbeat": datetime.utcnow(),
            "performance_metrics": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Mock async iteration
        mock_cursor.__aiter__.return_value = [agent_data]
        
        result = await agent_repo.get_healthy_agents()
        
        assert len(result) == 1
        assert result[0].name == "test-agent"
        assert result[0].status == AgentStatus.ONLINE
    
    @patch('app.db.repositories.get_database')
    async def test_update_heartbeat(self, mock_get_db, agent_repo):
        """Test updating agent heartbeat"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result
        
        result = await agent_repo.update_heartbeat("agent_id_123")
        
        assert result is True
        mock_collection.update_one.assert_called_once()


class TestDebateRepository:
    """Test debate repository operations"""
    
    @pytest.fixture
    def debate_repo(self):
        """Create debate repository instance"""
        return DebateRepository()
    
    @pytest.fixture
    def sample_debate(self):
        """Create sample debate thread for testing"""
        return DebateThread(
            workflow_id="workflow123",
            step_id="step123",
            participants=["agent1", "agent2"],
            status=DebateStatus.ACTIVE
        )
    
    @patch('app.db.repositories.get_database')
    async def test_create_debate(self, mock_get_db, debate_repo, sample_debate):
        """Test debate thread creation"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.inserted_id = "debate_id_123"
        mock_collection.insert_one.return_value = mock_result
        
        result = await debate_repo.create(sample_debate)
        
        assert result == "debate_id_123"
        mock_collection.insert_one.assert_called_once()
    
    @patch('app.db.repositories.get_database')
    async def test_get_debate_by_step_id(self, mock_get_db, debate_repo):
        """Test getting debate by step ID"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        debate_data = {
            "_id": "debate_id_123",
            "workflow_id": "workflow123",
            "step_id": "step123",
            "participants": ["agent1", "agent2"],
            "messages": [],
            "status": "active",
            "consensus_result": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mock_collection.find_one.return_value = debate_data
        
        result = await debate_repo.get_by_step_id("step123")
        
        assert result is not None
        assert result.step_id == "step123"
        assert result.workflow_id == "workflow123"


class TestResourceRepository:
    """Test resource repository operations"""
    
    @pytest.fixture
    def resource_repo(self):
        """Create resource repository instance"""
        return ResourceRepository()
    
    @pytest.fixture
    def sample_resource(self):
        """Create sample resource for testing"""
        return Resource(
            workflow_id="workflow123",
            type="document",
            content="Test document content",
            created_by="user123",
            tags=["important", "draft"]
        )
    
    @patch('app.db.repositories.get_database')
    async def test_create_resource(self, mock_get_db, resource_repo, sample_resource):
        """Test resource creation"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.inserted_id = "resource_id_123"
        mock_collection.insert_one.return_value = mock_result
        
        result = await resource_repo.create(sample_resource)
        
        assert result == "resource_id_123"
        mock_collection.insert_one.assert_called_once()
    
    @patch('app.db.repositories.get_database')
    async def test_get_resources_by_tags(self, mock_get_db, resource_repo):
        """Test getting resources by tags"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_collection.find.return_value = mock_cursor
        
        resource_data = {
            "_id": "resource_id_123",
            "workflow_id": "workflow123",
            "type": "document",
            "content": "Test content",
            "metadata": {},
            "tags": ["important", "draft"],
            "vector_embedding": None,
            "created_by": "user123",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "file_size": None,
            "mime_type": None,
            "original_filename": None
        }
        
        # Mock async iteration
        mock_cursor.__aiter__.return_value = [resource_data]
        
        result = await resource_repo.get_by_tags(["important"])
        
        assert len(result) == 1
        assert result[0].workflow_id == "workflow123"
        assert "important" in result[0].tags


class TestUserRepository:
    """Test user repository operations"""
    
    @pytest.fixture
    def user_repo(self):
        """Create user repository instance"""
        return UserRepository()
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing"""
        return User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123",
            is_active=True
        )
    
    @patch('app.db.repositories.get_database')
    async def test_create_user(self, mock_get_db, user_repo, sample_user):
        """Test user creation"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_result = MagicMock()
        mock_result.inserted_id = "user_id_123"
        mock_collection.insert_one.return_value = mock_result
        
        result = await user_repo.create(sample_user)
        
        assert result == "user_id_123"
        mock_collection.insert_one.assert_called_once()
    
    @patch('app.db.repositories.get_database')
    async def test_get_user_by_email(self, mock_get_db, user_repo):
        """Test getting user by email"""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        user_data = {
            "_id": "user_id_123",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed123",
            "is_active": True,
            "preferences": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        mock_collection.find_one.return_value = user_data
        
        result = await user_repo.get_by_email("test@example.com")
        
        assert result is not None
        assert result.email == "test@example.com"
        assert result.username == "testuser"