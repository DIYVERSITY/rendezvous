# Legacy task model - kept for backward compatibility
# New workflow models are in workflow.py

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class Task(BaseModel):
    """Legacy task model - use WorkflowStep instead for new implementations"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    name: str
    description: str
    status: str = "pending"  # pending, executing, completed, failed
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)