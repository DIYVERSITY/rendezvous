#!/usr/bin/env python3

# Test the models directly without imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("Testing direct model creation...")

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

# Test creation
print("Creating agent...")
agent = Agent(name="test", version="1.0", endpoint="http://test")
print(f"Agent created: {agent.name}")

# Test capability
capability = AgentCapability(
    name="test_cap",
    description="Test capability",
    input_schema={"type": "object"},
    output_schema={"type": "object"}
)
print(f"Capability created: {capability.name}")

print("All tests passed!")