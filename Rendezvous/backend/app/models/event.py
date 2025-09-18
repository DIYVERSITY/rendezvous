from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class EventType(str):
    AGENT_ACTION = "agent_action"
    USER_ACTION = "user_action"
    SYSTEM = "system"

class WorkflowEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    event_type: str
    step_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
