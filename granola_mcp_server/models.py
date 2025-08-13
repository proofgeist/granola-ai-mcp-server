"""Data models for Granola meeting information."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime


class MeetingMetadata(BaseModel):
    """Meeting metadata information."""
    id: str
    title: str
    date: datetime
    duration: Optional[int] = None
    participants: List[str] = []
    meeting_type: Optional[str] = None
    platform: Optional[str] = None


class MeetingDocument(BaseModel):
    """Meeting document information."""
    id: str
    meeting_id: str
    title: str
    content: str
    document_type: str
    created_at: datetime
    tags: List[str] = []


class MeetingTranscript(BaseModel):
    """Meeting transcript information."""
    meeting_id: str
    content: str
    speakers: List[str] = []
    language: Optional[str] = None
    confidence: Optional[float] = None


class CacheData(BaseModel):
    """Complete cache data structure."""
    meetings: Dict[str, MeetingMetadata] = {}
    documents: Dict[str, MeetingDocument] = {}
    transcripts: Dict[str, MeetingTranscript] = {}
    last_updated: Optional[datetime] = None