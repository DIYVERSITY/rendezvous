from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


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


class AgentAction(BaseModel):
    step: str
    agent_name: str
    input_data: dict
    output_data: dict = None
    timestamp: str


class AgentLog(BaseModel):
    workflow_id: str
    actions: list[AgentAction]