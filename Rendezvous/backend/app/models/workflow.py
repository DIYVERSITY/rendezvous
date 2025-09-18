from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


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
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
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
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
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
        """Add a step to the workflow and update total_steps"""
        self.steps.append(step)
        self.total_steps = len(self.steps)
        self.updated_at = datetime.utcnow()

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current step being executed"""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def advance_step(self) -> bool:
        """Advance to the next step, returns True if successful"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.updated_at = datetime.utcnow()
            return True
        return False

    def is_complete(self) -> bool:
        """Check if all steps are completed"""
        return all(step.status == StepStatus.COMPLETED for step in self.steps)

    def has_failed_steps(self) -> bool:
        """Check if any steps have failed"""
        return any(step.status == StepStatus.FAILED for step in self.steps)