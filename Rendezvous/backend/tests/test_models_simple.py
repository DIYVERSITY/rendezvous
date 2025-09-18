import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId


# Define models inline for testing
class WorkflowStatus(str, Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEBATING = "debating"


class WorkflowStep(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    step_number: int
    agent_id: str
    task_description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    status: StepStatus = StepStatus.PENDING
    reasoning: Optional[str] = None
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    debate_thread_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    prompt: str
    status: WorkflowStatus = WorkflowStatus.PLANNING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    agents_assigned: List[str] = Field(default_factory=list)
    current_step: int = 0
    total_steps: int = 0
    mind_map_data: Dict[str, Any] = Field(default_factory=dict)
    steps: List[WorkflowStep] = Field(default_factory=list)

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)
        self.total_steps = len(self.steps)
        self.updated_at = datetime.utcnow()

    def get_current_step(self) -> Optional[WorkflowStep]:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def advance_step(self) -> bool:
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.updated_at = datetime.utcnow()
            return True
        return False

    def is_complete(self) -> bool:
        return all(step.status == StepStatus.COMPLETED for step in self.steps)

    def has_failed_steps(self) -> bool:
        return any(step.status == StepStatus.FAILED for step in self.steps)


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    debate_enabled: bool = False


class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    version: str
    endpoint: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.OFFLINE
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_heartbeat(self) -> None:
        self.last_heartbeat = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_healthy(self, timeout_seconds: int = 300) -> bool:
        if self.status == AgentStatus.OFFLINE:
            return False
        time_since_heartbeat = datetime.utcnow() - self.last_heartbeat
        return time_since_heartbeat.total_seconds() < timeout_seconds

    def has_capability(self, capability_name: str) -> bool:
        return any(cap.name == capability_name for cap in self.capabilities)

    def get_capability(self, capability_name: str) -> Optional[AgentCapability]:
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap
        return None


# Test classes
class TestWorkflowModels:
    def test_workflow_creation(self):
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


class TestAgentModels:
    def test_agent_capability_creation(self):
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
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000"
        )
        
        original_heartbeat = agent.last_heartbeat
        
        # Add a small delay to ensure time difference
        import time
        time.sleep(0.001)
        
        agent.update_heartbeat()
        
        assert agent.last_heartbeat >= original_heartbeat

    def test_agent_health_check(self):
        agent = Agent(
            name="test-agent",
            version="1.0.0",
            endpoint="http://localhost:8000",
            status=AgentStatus.ONLINE
        )
        
        assert agent.is_healthy() is True
        
        agent.last_heartbeat = datetime.utcnow() - timedelta(minutes=10)
        assert agent.is_healthy(timeout_seconds=300) is False
        
        agent.status = AgentStatus.OFFLINE
        agent.last_heartbeat = datetime.utcnow()
        assert agent.is_healthy() is False

    def test_agent_capabilities(self):
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
        
        assert agent.has_capability("search") is True
        assert agent.has_capability("summarize") is True
        assert agent.has_capability("nonexistent") is False
        
        retrieved_cap = agent.get_capability("search")
        assert retrieved_cap is not None
        assert retrieved_cap.name == "search"
        
        assert agent.get_capability("nonexistent") is None