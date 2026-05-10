from typing import TypedDict, List, Optional
from datetime import datetime

class Task(TypedDict):
    id: Optional[int]
    title: str
    due_date: str
    priority: str
    status: str
    created_at: str

class Resource(TypedDict):
    id: Optional[int]
    name: str
    category: str
    location: str
    contact: str
    open_hours: str

class MoodLog(TypedDict):
    id: Optional[int]
    score: int
    note: str
    date: str
