from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class Resource(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
    )
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    type: str  # "document", "image", "url", "data", "svg"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    vector_embedding: Optional[List[float]] = None
    created_by: str  # Agent ID or user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    original_filename: Optional[str] = None

    def add_tag(self, tag: str) -> None:
        """Add a tag to the resource"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the resource"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def has_tag(self, tag: str) -> bool:
        """Check if resource has a specific tag"""
        return tag in self.tags

    def update_metadata(self, key: str, value: Any) -> None:
        """Update a metadata field"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def is_image(self) -> bool:
        """Check if resource is an image"""
        return self.type == "image" or (self.mime_type and self.mime_type.startswith("image/"))

    def is_document(self) -> bool:
        """Check if resource is a document"""
        return self.type == "document"

    def is_url(self) -> bool:
        """Check if resource is a URL"""
        return self.type == "url"

    def get_file_extension(self) -> Optional[str]:
        """Get file extension from original filename"""
        if self.original_filename and "." in self.original_filename:
            return self.original_filename.split(".")[-1].lower()
        return None