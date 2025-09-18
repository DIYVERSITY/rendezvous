from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class DebateStatus(str, Enum):
    ACTIVE = "active"
    CONSENSUS_REACHED = "consensus_reached"
    ESCALATED = "escalated"


class CoralMessage(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    sender_did: str
    receiver_did: str
    intent: str  # "request", "debate", "resource_share", "consensus"
    content: Dict[str, Any]
    thread_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signature: str

    def validate_intent(self) -> bool:
        """Validate that the intent is one of the allowed values"""
        allowed_intents = ["request", "debate", "resource_share", "consensus", "challenge", "support"]
        return self.intent in allowed_intents

    def is_debate_message(self) -> bool:
        """Check if this message is part of a debate"""
        return self.intent in ["debate", "challenge", "support", "consensus"]


class DebateThread(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    step_id: str
    participants: List[str] = Field(default_factory=list)  # Agent IDs
    messages: List[CoralMessage] = Field(default_factory=list)
    status: DebateStatus = DebateStatus.ACTIVE
    consensus_result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_message(self, message: CoralMessage) -> None:
        """Add a message to the debate thread"""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def add_participant(self, agent_id: str) -> None:
        """Add a participant to the debate"""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.updated_at = datetime.utcnow()

    def get_messages_by_agent(self, agent_id: str) -> List[CoralMessage]:
        """Get all messages from a specific agent"""
        return [msg for msg in self.messages if msg.sender_did == agent_id]

    def has_consensus(self) -> bool:
        """Check if consensus has been reached"""
        return self.status == DebateStatus.CONSENSUS_REACHED

    def reach_consensus(self, result: Dict[str, Any]) -> None:
        """Mark the debate as having reached consensus"""
        self.status = DebateStatus.CONSENSUS_REACHED
        self.consensus_result = result
        self.updated_at = datetime.utcnow()

    def escalate(self) -> None:
        """Escalate the debate to user intervention"""
        self.status = DebateStatus.ESCALATED
        self.updated_at = datetime.utcnow()