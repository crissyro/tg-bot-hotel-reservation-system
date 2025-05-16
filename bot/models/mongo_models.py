from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Review(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    text: str
    rating: int = Field(ge=0, le=10)
    created_at: datetime = datetime.now()
    is_approved: bool = False
    admin_comment: Optional[str] = None