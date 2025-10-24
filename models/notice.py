from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Notice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    author: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    view_count: int = Field(default=0)
