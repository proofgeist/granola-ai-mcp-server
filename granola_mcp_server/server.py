"""Granola MCP Server implementation."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    TextContent,
    Tool,
)

from .models import CacheData, MeetingMetadata, MeetingDocument, MeetingTranscript


class GranolaMCPServer:
    """Granola MCP Server for meeting intelligence queries."""
    
    def __init__(self, cache_path: Optional[str] = None):
        """Initialize the Granola MCP server."""
        if cache_path is None:
            cache_path = os.path.expanduser("~/Library/Application Support/Granola/cache-v3.json")
        
        self.cache_path = cache_path
        self.server = Server("granola-mcp-server")
        self.cache_data: Optional[CacheData] = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_meetings",
                    description="Search meetings by title, content, or participants",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for meetings"
                            },
                            "limit": {
                                "type": "integer", 
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_meeting_details",
                    description="Get detailed information about a specific meeting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "meeting_id": {
                                "type": "string",
                                "description": "Meeting ID to retrieve details for"
                            }
                        },
                        "required": ["meeting_id"]
                    }
                ),
                Tool(
                    name="get_meeting_transcript",
                    description="Get transcript for a specific meeting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "meeting_id": {
                                "type": "string", 
                                "description": "Meeting ID to get transcript for"
                            }
                        },
                        "required": ["meeting_id"]
                    }
                ),
                Tool(
                    name="get_meeting_documents",
                    description="Get documents associated with a meeting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "meeting_id": {
                                "type": "string",
                                "description": "Meeting ID to get documents for" 
                            }
                        },
                        "required": ["meeting_id"]
                    }
                ),
                Tool(
                    name="analyze_meeting_patterns",
                    description="Analyze patterns across multiple meetings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_type": {
                                "type": "string",
                                "description": "Type of pattern to analyze (topics, participants, frequency)",
                                "enum": ["topics", "participants", "frequency"]
                            },
                            "date_range": {
                                "type": "object",
                                "properties": {
                                    "start_date": {"type": "string", "format": "date"},
                                    "end_date": {"type": "string", "format": "date"}
                                },
                                "description": "Optional date range for analysis"
                            }
                        },
                        "required": ["pattern_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            await self._ensure_cache_loaded()
            
            if name == "search_meetings":
                return await self._search_meetings(
                    query=arguments["query"],
                    limit=arguments.get("limit", 10)
                )
            elif name == "get_meeting_details":
                return await self._get_meeting_details(arguments["meeting_id"])
            elif name == "get_meeting_transcript":
                return await self._get_meeting_transcript(arguments["meeting_id"])
            elif name == "get_meeting_documents":
                return await self._get_meeting_documents(arguments["meeting_id"])
            elif name == "analyze_meeting_patterns":
                return await self._analyze_meeting_patterns(
                    pattern_type=arguments["pattern_type"],
                    date_range=arguments.get("date_range")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _ensure_cache_loaded(self):
        """Ensure cache data is loaded."""
        if self.cache_data is None:
            await self._load_cache()
    
    async def _load_cache(self):
        """Load and parse Granola cache data."""
        try:
            cache_path = Path(self.cache_path)
            if not cache_path.exists():
                self.cache_data = CacheData()
                return
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Handle Granola's nested cache structure
            if 'cache' in raw_data and isinstance(raw_data['cache'], str):
                # Cache data is stored as a JSON string inside the 'cache' key
                actual_data = json.loads(raw_data['cache'])
                if 'state' in actual_data:
                    raw_data = actual_data['state']
                else:
                    raw_data = actual_data
            
            self.cache_data = await self._parse_cache_data(raw_data)
            
        except Exception as e:
            self.cache_data = CacheData()
            print(f"Error loading cache: {e}")
    
    async def _parse_cache_data(self, raw_data: Dict[str, Any]) -> CacheData:
        """Parse raw cache data into structured models."""
        cache_data = CacheData()
        
        # Parse Granola documents (which are meetings)
        if "documents" in raw_data:
            for meeting_id, meeting_data in raw_data["documents"].items():
                try:
                    # Extract participants from people array
                    participants = []
                    if "people" in meeting_data and isinstance(meeting_data["people"], list):
                        participants = [person.get("name", "") for person in meeting_data["people"] if person.get("name")]
                    
                    # Parse creation date
                    created_at = meeting_data.get("created_at")
                    if created_at:
                        # Handle Granola's ISO format
                        if created_at.endswith('Z'):
                            created_at = created_at[:-1] + '+00:00'
                        meeting_date = datetime.fromisoformat(created_at)
                    else:
                        meeting_date = datetime.now()
                    
                    metadata = MeetingMetadata(
                        id=meeting_id,
                        title=meeting_data.get("title", "Untitled Meeting"),
                        date=meeting_date,
                        duration=None,  # Granola doesn't store duration in this format
                        participants=participants,
                        meeting_type=meeting_data.get("type", "meeting"),
                        platform=None  # Not stored in Granola cache
                    )
                    cache_data.meetings[meeting_id] = metadata
                except Exception as e:
                    print(f"Error parsing meeting {meeting_id}: {e}")
        
        # Parse Granola transcripts
        if "transcripts" in raw_data:
            for transcript_id, transcript_data in raw_data["transcripts"].items():
                try:
                    # Find corresponding meeting ID
                    meeting_id = transcript_data.get("document_id") or transcript_id
                    
                    # Extract transcript content and speakers
                    content = ""
                    speakers = []
                    
                    if isinstance(transcript_data, dict):
                        # Handle different transcript formats
                        if "content" in transcript_data:
                            content = transcript_data["content"]
                        elif "text" in transcript_data:
                            content = transcript_data["text"]
                        elif "transcript" in transcript_data:
                            content = transcript_data["transcript"]
                        
                        # Extract speakers if available
                        if "speakers" in transcript_data:
                            speakers = transcript_data["speakers"]
                        elif "people" in transcript_data:
                            speakers = [person.get("name", "") for person in transcript_data["people"] if person.get("name")]
                    
                    if content:  # Only create transcript if we have content
                        transcript = MeetingTranscript(
                            meeting_id=meeting_id,
                            content=content,
                            speakers=speakers,
                            language=transcript_data.get("language"),
                            confidence=transcript_data.get("confidence")
                        )
                        cache_data.transcripts[meeting_id] = transcript
                except Exception as e:
                    print(f"Error parsing transcript {transcript_id}: {e}")
        
        # Extract document content from Granola documents
        if "documents" in raw_data:
            for doc_id, doc_data in raw_data["documents"].items():
                try:
                    # Extract content from various Granola fields
                    content_parts = []
                    
                    # Try notes_plain first (cleanest format)
                    if doc_data.get("notes_plain"):
                        content_parts.append(doc_data["notes_plain"])
                    
                    # Try notes_markdown as backup
                    elif doc_data.get("notes_markdown"):
                        content_parts.append(doc_data["notes_markdown"])
                    
                    # Try to extract from structured notes field
                    elif doc_data.get("notes") and isinstance(doc_data["notes"], dict):
                        notes_content = self._extract_structured_notes(doc_data["notes"])
                        if notes_content:
                            content_parts.append(notes_content)
                    
                    # Add overview if available
                    if doc_data.get("overview"):
                        content_parts.append(f"Overview: {doc_data['overview']}")
                    
                    # Add summary if available  
                    if doc_data.get("summary"):
                        content_parts.append(f"Summary: {doc_data['summary']}")
                    
                    content = "\n\n".join(content_parts)
                    
                    # Only create document if we have a meeting for it
                    if doc_id in cache_data.meetings:
                        meeting = cache_data.meetings[doc_id]
                        document = MeetingDocument(
                            id=doc_id,
                            meeting_id=doc_id,
                            title=meeting.title,
                            content=content,
                            document_type="meeting_notes",
                            created_at=meeting.date,
                            tags=[]
                        )
                        cache_data.documents[doc_id] = document
                        
                except Exception as e:
                    print(f"Error extracting document content for {doc_id}: {e}")
        
        cache_data.last_updated = datetime.now()
        return cache_data
    
    def _extract_structured_notes(self, notes_data: Dict[str, Any]) -> str:
        """Extract text content from Granola's structured notes format."""
        try:
            if not isinstance(notes_data, dict) or 'content' not in notes_data:
                return ""
            
            def extract_text_from_content(content_list):
                text_parts = []
                if isinstance(content_list, list):
                    for item in content_list:
                        if isinstance(item, dict):
                            # Handle different content types
                            if item.get('type') == 'paragraph' and 'content' in item:
                                text_parts.append(extract_text_from_content(item['content']))
                            elif item.get('type') == 'text' and 'text' in item:
                                text_parts.append(item['text'])
                            elif 'content' in item:
                                text_parts.append(extract_text_from_content(item['content']))
                return ' '.join(text_parts)
            
            return extract_text_from_content(notes_data['content'])
            
        except Exception as e:
            print(f"Error extracting structured notes: {e}")
            return ""
    
    async def _search_meetings(self, query: str, limit: int = 10) -> List[TextContent]:
        """Search meetings by query."""
        if not self.cache_data:
            return [TextContent(type="text", text="No meeting data available")]
        
        query_lower = query.lower()
        results = []
        
        for meeting_id, meeting in self.cache_data.meetings.items():
            score = 0
            
            # Search in title
            if query_lower in meeting.title.lower():
                score += 2
            
            # Search in participants
            for participant in meeting.participants:
                if query_lower in participant.lower():
                    score += 1
            
            # Search in transcript content if available
            if meeting_id in self.cache_data.transcripts:
                transcript = self.cache_data.transcripts[meeting_id]
                if query_lower in transcript.content.lower():
                    score += 1
            
            if score > 0:
                results.append((score, meeting))
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x[0], reverse=True)
        results = results[:limit]
        
        if not results:
            return [TextContent(type="text", text=f"No meetings found matching '{query}'")]
        
        output_lines = [f"Found {len(results)} meeting(s) matching '{query}':\n"]
        
        for score, meeting in results:
            output_lines.append(f"• **{meeting.title}** ({meeting.id})")
            output_lines.append(f"  Date: {meeting.date.strftime('%Y-%m-%d %H:%M')}")
            if meeting.participants:
                output_lines.append(f"  Participants: {', '.join(meeting.participants)}")
            output_lines.append("")
        
        return [TextContent(type="text", text="\n".join(output_lines))]
    
    async def _get_meeting_details(self, meeting_id: str) -> List[TextContent]:
        """Get detailed meeting information."""
        if not self.cache_data or meeting_id not in self.cache_data.meetings:
            return [TextContent(type="text", text=f"Meeting '{meeting_id}' not found")]
        
        meeting = self.cache_data.meetings[meeting_id]
        
        details = [
            f"# Meeting Details: {meeting.title}\n",
            f"**ID:** {meeting.id}",
            f"**Date:** {meeting.date.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if meeting.duration:
            details.append(f"**Duration:** {meeting.duration} minutes")
        
        if meeting.participants:
            details.append(f"**Participants:** {', '.join(meeting.participants)}")
        
        if meeting.meeting_type:
            details.append(f"**Type:** {meeting.meeting_type}")
        
        if meeting.platform:
            details.append(f"**Platform:** {meeting.platform}")
        
        # Add document count
        doc_count = sum(1 for doc in self.cache_data.documents.values() 
                       if doc.meeting_id == meeting_id)
        if doc_count > 0:
            details.append(f"**Documents:** {doc_count}")
        
        # Add transcript availability
        if meeting_id in self.cache_data.transcripts:
            details.append("**Transcript:** Available")
        
        return [TextContent(type="text", text="\n".join(details))]
    
    async def _get_meeting_transcript(self, meeting_id: str) -> List[TextContent]:
        """Get meeting transcript."""
        if not self.cache_data:
            return [TextContent(type="text", text="No meeting data available")]
        
        if meeting_id not in self.cache_data.transcripts:
            return [TextContent(type="text", text=f"No transcript available for meeting '{meeting_id}'")]
        
        transcript = self.cache_data.transcripts[meeting_id]
        meeting = self.cache_data.meetings.get(meeting_id)
        
        output = [f"# Transcript: {meeting.title if meeting else meeting_id}\n"]
        
        if transcript.speakers:
            output.append(f"**Speakers:** {', '.join(transcript.speakers)}")
        
        if transcript.language:
            output.append(f"**Language:** {transcript.language}")
        
        if transcript.confidence:
            output.append(f"**Confidence:** {transcript.confidence:.2%}")
        
        output.append("\n## Transcript Content\n")
        output.append(transcript.content)
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _get_meeting_documents(self, meeting_id: str) -> List[TextContent]:
        """Get meeting documents."""
        if not self.cache_data:
            return [TextContent(type="text", text="No meeting data available")]
        
        documents = [doc for doc in self.cache_data.documents.values() 
                    if doc.meeting_id == meeting_id]
        
        if not documents:
            return [TextContent(type="text", text=f"No documents found for meeting '{meeting_id}'")]
        
        meeting = self.cache_data.meetings.get(meeting_id)
        output = [f"# Documents: {meeting.title if meeting else meeting_id}\n"]
        output.append(f"Found {len(documents)} document(s):\n")
        
        for doc in documents:
            output.append(f"## {doc.title}")
            output.append(f"**Type:** {doc.document_type}")
            output.append(f"**Created:** {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            if doc.tags:
                output.append(f"**Tags:** {', '.join(doc.tags)}")
            
            output.append(f"\n{doc.content}\n")
            output.append("---\n")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _analyze_meeting_patterns(self, pattern_type: str, date_range: Optional[Dict] = None) -> List[TextContent]:
        """Analyze patterns across meetings."""
        if not self.cache_data:
            return [TextContent(type="text", text="No meeting data available")]
        
        meetings = list(self.cache_data.meetings.values())
        
        # Filter by date range if provided
        if date_range:
            start_date = datetime.fromisoformat(date_range.get("start_date", "1900-01-01"))
            end_date = datetime.fromisoformat(date_range.get("end_date", "2100-01-01"))
            meetings = [m for m in meetings if start_date <= m.date <= end_date]
        
        if pattern_type == "participants":
            return await self._analyze_participant_patterns(meetings)
        elif pattern_type == "frequency":
            return await self._analyze_frequency_patterns(meetings)
        elif pattern_type == "topics":
            return await self._analyze_topic_patterns(meetings)
        else:
            return [TextContent(type="text", text=f"Unknown pattern type: {pattern_type}")]
    
    async def _analyze_participant_patterns(self, meetings: List[MeetingMetadata]) -> List[TextContent]:
        """Analyze participant patterns."""
        participant_counts = {}
        
        for meeting in meetings:
            for participant in meeting.participants:
                participant_counts[participant] = participant_counts.get(participant, 0) + 1
        
        if not participant_counts:
            return [TextContent(type="text", text="No participant data found")]
        
        sorted_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)
        
        output = [
            f"# Participant Analysis ({len(meetings)} meetings)\n",
            "## Most Active Participants\n"
        ]
        
        for participant, count in sorted_participants[:10]:
            output.append(f"• **{participant}:** {count} meetings")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _analyze_frequency_patterns(self, meetings: List[MeetingMetadata]) -> List[TextContent]:
        """Analyze meeting frequency patterns."""
        if not meetings:
            return [TextContent(type="text", text="No meetings found for analysis")]
        
        # Group by month
        monthly_counts = {}
        for meeting in meetings:
            month_key = meeting.date.strftime("%Y-%m")
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        output = [
            f"# Meeting Frequency Analysis ({len(meetings)} meetings)\n",
            "## Meetings by Month\n"
        ]
        
        for month, count in sorted(monthly_counts.items()):
            output.append(f"• **{month}:** {count} meetings")
        
        avg_per_month = len(meetings) / len(monthly_counts) if monthly_counts else 0
        output.append(f"\n**Average per month:** {avg_per_month:.1f}")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _analyze_topic_patterns(self, meetings: List[MeetingMetadata]) -> List[TextContent]:
        """Analyze topic patterns from meeting titles."""
        if not meetings:
            return [TextContent(type="text", text="No meetings found for analysis")]
        
        # Simple keyword extraction from titles
        word_counts = {}
        for meeting in meetings:
            words = meeting.title.lower().split()
            for word in words:
                # Filter out common words
                if len(word) > 3 and word not in ['meeting', 'call', 'sync', 'with']:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        if not word_counts:
            return [TextContent(type="text", text="No significant topics found in meeting titles")]
        
        sorted_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        output = [
            f"# Topic Analysis ({len(meetings)} meetings)\n",
            "## Most Common Topics (from titles)\n"
        ]
        
        for topic, count in sorted_topics[:15]:
            output.append(f"• **{topic}:** {count} mentions")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    def run(self, transport_type: str = "stdio"):
        """Run the server."""
        import asyncio
        from mcp.server.stdio import stdio_server
        from mcp.types import ServerCapabilities
        
        if transport_type == "stdio":
            async def main():
                # Set up server capabilities for tool support
                capabilities = ServerCapabilities(
                    tools={}  # Empty dict indicates tool support is available
                )
                
                options = InitializationOptions(
                    server_name="granola-mcp-server",
                    server_version="0.1.0",
                    capabilities=capabilities
                )
                
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(read_stream, write_stream, options)
            
            return asyncio.run(main())
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}. Only 'stdio' is supported.")


def main():
    """Main entry point for the server."""
    server = GranolaMCPServer()
    server.run()