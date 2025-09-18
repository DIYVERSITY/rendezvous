import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.workflow import Workflow, WorkflowStep, WorkflowStatus, StepStatus
from app.models.agent import Agent, AgentCapability, AgentStatus
from app.models.debate import DebateThread, DebateStatus, CoralMessage
from app.models.resource import Resource
from app.models.user import User


class TestWorkflowModels:
    """Test workflow-related models"""
    
    def test_workflow_creation(self):
        """Test basic workflow creation"""
        workflow = Workflow(
            user_id="user123",
            prompt="Test workflow prompt"
        )
        
        assert workflow.user_id == "user123"
        assert workflow.prompt == "Test workflow prompt"
        assert workflow.status == WorkflowStatus.PLANNING
        assert workflow.current_step == 0
        assert workflow.total_steps == 0
        assert len(workflow.steps) == 0
        assert isinstance(workflow.created_at, datetime)
        assert isinstance(workflow.updated_at, datetime)
    
    def test_workflow_step_creation(self):
        """Test workflow step creation"""
        step = WorkflowStep(
            workflow_id="workflow123",
            step_number=1,
            agent_id="agent123",
            task_description="Test task"
        )
        
        assert step.workflow_id == "workflow123"
        assert step.step_number == 1
        assert step.agent_id == "agent123"
        assert step.task_description == "Test task"
        assert step.status == StepStatus.PENDING
        assert step.output_data is None
        assert step.reasoning is None
        assert len(step.alternatives) == 0
    
    def test_workflow_add_step(self):
        """Test adding steps to workflow"""
        workflow = Workflow(user_id="user123", prompt="Test")
        
        step1 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=1,
            agent_id="agent1",
            task_description="Step 1"
        )
        
        step2 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=2,
            agent_id="agent2", 
            task_description="Step 2"
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        assert len(workflow.steps) == 2
        assert workflow.total_steps == 2
        assert workflow.steps[0].step_number == 1
        assert workflow.steps[1].step_number == 2
    
    def test_workflow_get_current_step(self):
        """Test getting current step"""
        workflow = Workflow(user_id="user123", prompt="Test")
        
        # No steps
        assert workflow.get_current_step() is None
        
        # Add steps
        step1 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=1,
            agent_id="agent1",
            task_description="Step 1"
        )
        workflow.add_step(step1)
        
        # Current step should be first step
        current = workflow.get_current_step()
        assert current is not None
        assert current.step_number == 1
    
    def test_workflow_advance_step(self):
        """Test advancing workflow steps"""
        workflow = Workflow(user_id="user123", prompt="Test")
        
        step1 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=1,
            agent_id="agent1",
            task_description="Step 1"
        )
        step2 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=2,
            agent_id="agent2",
            task_description="Step 2"
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        # Should start at step 0
        assert workflow.current_step == 0
        
        # Advance to step 1
        result = workflow.advance_step()
        assert result is True
        assert workflow.current_step == 1
        
        # Try to advance beyond last step
        result = workflow.advance_step()
        assert result is False
        assert workflow.current_step == 1
    
    def test_workflow_completion_status(self):
        """Test workflow completion checking"""
        workflow = Workflow(user_id="user123", prompt="Test")
        
        step1 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=1,
            agent_id="agent1",
            task_description="Step 1",
            status=StepStatus.COMPLETED
        )
        step2 = WorkflowStep(
            workflow_id=workflow.id,
            step_number=2,
            agent_id="agent2",
            task_description="Step 2",
            status=StepStatus.PENDING
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        # Not complete yet
        assert workflow.is_complete() is False
        assert workflow.has_failed_steps() is False
        
        # Complete second step
        step2.status = StepStatus.COMPLETED
        assert workflow.is_complete() is True
        
        # Fail a step
        step2.status = StepStatus.FAILED
        assert workflow.has_failed_steps() is True


class TestAgentModels:
    """Test agent-related models"""
    
    def test_agent_capability_creation(self):
        """Test agent capability creation"""
        capability = AgentCapability(
            name="test_capability",
            description="Test capability",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            debate_enabled=True
        )
        
        assert capability.name == "test_capability"
        assert capability.description == "Test capability"
        assert capability.debate_enabled is True
    
    def test_agent_creation(self):
        """Test agent creation"""
        capability = AgentCapability(
            name="search",
            description="Search capability",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000",
            capabilities=[capability]
        )
        
        assert agent.name == "test-agent"
        assert agent.version == "1.0.0"
        assert agent.endpoint == "http://localhost:8000"
        assert agent.status == AgentStatus.OFFLINE
        assert len(agent.capabilities) == 1
        assert isinstance(agent.performance_metrics, dict)
    
    def test_agent_heartbeat(self):
        """Test agent heartbeat functionality"""
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000"
        )
        
        original_heartbeat = agent.last_heartbeat
        
        # Update heartbeat
        agent.update_heartbeat()
        
        assert agent.last_heartbeat > original_heartbeat
    
    def test_agent_health_check(self):
        """Test agent health checking"""
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000",
            status=AgentStatus.ONLINE
        )
        
        # Should be healthy with recent heartbeat
        assert agent.is_healthy() is True
        
        # Set old heartbeat
        agent.last_heartbeat = datetime.utcnow() - timedelta(minutes=10)
        assert agent.is_healthy(timeout_seconds=300) is False
        
        # Offline agent should not be healthy
        agent.status = AgentStatus.OFFLINE
        agent.last_heartbeat = datetime.utcnow()
        assert agent.is_healthy() is False
    
    def test_agent_capabilities(self):
        """Test agent capability management"""
        search_cap = AgentCapability(
            name="search",
            description="Search capability",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        summarize_cap = AgentCapability(
            name="summarize",
            description="Summarize capability", 
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000",
            capabilities=[search_cap, summarize_cap]
        )
        
        # Test capability checking
        assert agent.has_capability("search") is True
        assert agent.has_capability("summarize") is True
        assert agent.has_capability("nonexistent") is False
        
        # Test capability retrieval
        retrieved_cap = agent.get_capability("search")
        assert retrieved_cap is not None
        assert retrieved_cap.name == "search"
        
        assert agent.get_capability("nonexistent") is None


class TestDebateModels:
    """Test debate-related models"""
    
    def test_coral_message_creation(self):
        """Test Coral message creation"""
        message = CoralMessage(
            sender_did="agent1",
            receiver_did="agent2",
            intent="request",
            content={"task": "test"},
            thread_id="thread123",
            signature="signature123"
        )
        
        assert message.sender_did == "agent1"
        assert message.receiver_did == "agent2"
        assert message.intent == "request"
        assert message.content == {"task": "test"}
        assert message.thread_id == "thread123"
        assert isinstance(message.timestamp, datetime)
    
    def test_coral_message_validation(self):
        """Test Coral message validation"""
        message = CoralMessage(
            sender_did="agent1",
            receiver_did="agent2",
            intent="request",
            content={},
            thread_id="thread123",
            signature="sig123"
        )
        
        assert message.validate_intent() is True
        assert message.is_debate_message() is False
        
        # Test debate message
        message.intent = "debate"
        assert message.is_debate_message() is True
    
    def test_debate_thread_creation(self):
        """Test debate thread creation"""
        debate = DebateThread(
            workflow_id="workflow123",
            step_id="step123"
        )
        
        assert debate.workflow_id == "workflow123"
        assert debate.step_id == "step123"
        assert debate.status == DebateStatus.ACTIVE
        assert len(debate.participants) == 0
        assert len(debate.messages) == 0
        assert debate.consensus_result is None
    
    def test_debate_thread_participants(self):
        """Test debate thread participant management"""
        debate = DebateThread(
            workflow_id="workflow123",
            step_id="step123"
        )
        
        # Add participants
        debate.add_participant("agent1")
        debate.add_participant("agent2")
        debate.add_participant("agent1")  # Duplicate should be ignored
        
        assert len(debate.participants) == 2
        assert "agent1" in debate.participants
        assert "agent2" in debate.participants
    
    def test_debate_thread_messages(self):
        """Test debate thread message management"""
        debate = DebateThread(
            workflow_id="workflow123",
            step_id="step123"
        )
        
        message1 = CoralMessage(
            sender_did="agent1",
            receiver_did="agent2",
            intent="debate",
            content={"argument": "test1"},
            thread_id=debate.id,
            signature="sig1"
        )
        
        message2 = CoralMessage(
            sender_did="agent2",
            receiver_did="agent1",
            intent="debate",
            content={"argument": "test2"},
            thread_id=debate.id,
            signature="sig2"
        )
        
        debate.add_message(message1)
        debate.add_message(message2)
        
        assert len(debate.messages) == 2
        
        # Get messages by agent
        agent1_messages = debate.get_messages_by_agent("agent1")
        assert len(agent1_messages) == 1
        assert agent1_messages[0].content["argument"] == "test1"
    
    def test_debate_consensus(self):
        """Test debate consensus functionality"""
        debate = DebateThread(
            workflow_id="workflow123",
            step_id="step123"
        )
        
        assert debate.has_consensus() is False
        
        # Reach consensus
        result = {"decision": "approved", "votes": {"agent1": "yes", "agent2": "yes"}}
        debate.reach_consensus(result)
        
        assert debate.has_consensus() is True
        assert debate.status == DebateStatus.CONSENSUS_REACHED
        assert debate.consensus_result == result
    
    def test_debate_escalation(self):
        """Test debate escalation"""
        debate = DebateThread(
            workflow_id="workflow123",
            step_id="step123"
        )
        
        debate.escalate()
        assert debate.status == DebateStatus.ESCALATED


class TestResourceModel:
    """Test resource model"""
    
    def test_resource_creation(self):
        """Test resource creation"""
        resource = Resource(
            workflow_id="workflow123",
            type="document",
            content="Test content",
            created_by="user123"
        )
        
        assert resource.workflow_id == "workflow123"
        assert resource.type == "document"
        assert resource.content == "Test content"
        assert resource.created_by == "user123"
        assert len(resource.tags) == 0
        assert isinstance(resource.metadata, dict)
    
    def test_resource_tags(self):
        """Test resource tag management"""
        resource = Resource(
            workflow_id="workflow123",
            type="document",
            content="Test content",
            created_by="user123"
        )
        
        # Add tags
        resource.add_tag("important")
        resource.add_tag("draft")
        resource.add_tag("important")  # Duplicate should be ignored
        
        assert len(resource.tags) == 2
        assert resource.has_tag("important") is True
        assert resource.has_tag("draft") is True
        assert resource.has_tag("nonexistent") is False
        
        # Remove tag
        resource.remove_tag("draft")
        assert len(resource.tags) == 1
        assert resource.has_tag("draft") is False
    
    def test_resource_metadata(self):
        """Test resource metadata management"""
        resource = Resource(
            workflow_id="workflow123",
            type="document",
            content="Test content",
            created_by="user123"
        )
        
        resource.update_metadata("author", "John Doe")
        resource.update_metadata("version", "1.0")
        
        assert resource.metadata["author"] == "John Doe"
        assert resource.metadata["version"] == "1.0"
    
    def test_resource_type_checking(self):
        """Test resource type checking methods"""
        image_resource = Resource(
            workflow_id="workflow123",
            type="image",
            content="image_data",
            created_by="user123",
            mime_type="image/png"
        )
        
        doc_resource = Resource(
            workflow_id="workflow123",
            type="document",
            content="document_content",
            created_by="user123"
        )
        
        url_resource = Resource(
            workflow_id="workflow123",
            type="url",
            content="https://example.com",
            created_by="user123"
        )
        
        assert image_resource.is_image() is True
        assert image_resource.is_document() is False
        assert image_resource.is_url() is False
        
        assert doc_resource.is_document() is True
        assert doc_resource.is_image() is False
        
        assert url_resource.is_url() is True
        assert url_resource.is_image() is False
    
    def test_resource_file_extension(self):
        """Test file extension extraction"""
        resource = Resource(
            workflow_id="workflow123",
            type="document",
            content="content",
            created_by="user123",
            original_filename="document.pdf"
        )
        
        assert resource.get_file_extension() == "pdf"
        
        resource.original_filename = "image.PNG"
        assert resource.get_file_extension() == "png"
        
        resource.original_filename = "noextension"
        assert resource.get_file_extension() is None


class TestUserModel:
    """Test user model"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed123"
        assert user.is_active is True
        assert isinstance(user.preferences, dict)
        assert user.last_login is None
    
    def test_user_login_tracking(self):
        """Test user login tracking"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123"
        )
        
        assert user.last_login is None
        
        user.update_last_login()
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
    
    def test_user_preferences(self):
        """Test user preference management"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed123"
        )
        
        # Set preferences
        user.update_preference("theme", "dark")
        user.update_preference("notifications", True)
        
        assert user.get_preference("theme") == "dark"
        assert user.get_preference("notifications") is True
        assert user.get_preference("nonexistent", "default") == "default"