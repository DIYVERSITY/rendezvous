#!/usr/bin/env python3

try:
    print("Testing imports...")
    
    print("1. Importing datetime...")
    from datetime import datetime
    print("   ✓ datetime imported")
    
    print("2. Importing enum...")
    from enum import Enum
    print("   ✓ enum imported")
    
    print("3. Importing typing...")
    from typing import List, Dict, Any, Optional
    print("   ✓ typing imported")
    
    print("4. Importing pydantic...")
    from pydantic import BaseModel, Field, ConfigDict
    print("   ✓ pydantic imported")
    
    print("5. Importing bson...")
    from bson import ObjectId
    print("   ✓ bson imported")
    
    print("6. Testing AgentStatus...")
    class AgentStatus(str, Enum):
        ONLINE = "online"
        OFFLINE = "offline"
        BUSY = "busy"
    print("   ✓ AgentStatus created")
    
    print("7. Testing AgentCapability...")
    class AgentCapability(BaseModel):
        model_config = ConfigDict(
            json_encoders={
                ObjectId: str
            }
        )
        
        name: str
        description: str
        input_schema: Dict[str, Any]
        output_schema: Dict[str, Any]
        debate_enabled: bool = False
    print("   ✓ AgentCapability created")
    
    print("8. Testing Agent...")
    class Agent(BaseModel):
        model_config = ConfigDict(
            use_enum_values=True,
            json_encoders={
                datetime: lambda v: v.isoformat(),
                ObjectId: str
            }
        )
        
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
    print("   ✓ Agent created")
    
    print("9. Testing Agent instantiation...")
    agent = Agent(name="test", version="1.0", endpoint="http://test")
    print(f"   ✓ Agent instantiated: {agent.name}")
    
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()