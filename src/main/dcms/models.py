"""Pydantic request/response models for the REST API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ProblemCreate(BaseModel):
    problem_id: str
    title: str
    statement: str = ""
    time_limit: float = 2.0
    memory_limit: int = 256
    difficulty: str = "medium"
    points: int = 100
    sample_input: str = ""
    sample_output: str = ""
    input_format: str = ""
    output_format: str = ""
    constraints: str = ""


class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    statement: Optional[str] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    difficulty: Optional[str] = None
    points: Optional[int] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None


class TestCaseCreate(BaseModel):
    input_data: str = ""
    expected_output: str
    is_sample: bool = False
    points: int = 0


class AnnouncementCreate(BaseModel):
    title: str
    content: str = ""
    priority: str = "normal"


class BroadcastMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
