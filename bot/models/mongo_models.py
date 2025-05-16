from pydantic import BaseModel, Field
from datetime import datetime

class Review(BaseModel):
    user_id: int
    text: str
    rating: int = Field(ge=0, le=10)
    created_at: datetime = datetime.now()
    is_approved: bool = False