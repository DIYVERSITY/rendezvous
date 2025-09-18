from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId


class User(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_preference(self, key: str, value: Any) -> None:
        """Update a user preference"""
        self.preferences[key] = value
        self.updated_at = datetime.utcnow()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference with optional default"""
        return self.preferences.get(key, default)