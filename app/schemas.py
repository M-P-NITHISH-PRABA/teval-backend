from pydantic import BaseModel, Field
from typing import Optional

class FeedbackIn(BaseModel):
    session_id: str
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None
    text: str = Field(..., min_length=1)
