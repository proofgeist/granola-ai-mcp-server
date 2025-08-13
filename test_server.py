#!/usr/bin/env python3
"""Test script for Granola MCP Server."""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path

from granola_mcp_server.server import GranolaMCPServer


async def create_test_cache():
    """Create a test cache file."""
    test_data = {
        "meetings": {
            "meeting_1": {
                "title": "Weekly Team Standup",
                "date": "2024-01-15T10:00:00",
                "duration": 30,
                "participants": ["Alice", "Bob", "Charlie"],
                "type": "standup",
                "platform": "Zoom"
            },
            "meeting_2": {
                "title": "Q1 Planning Session",
                "date": "2024-01-20T14:00:00", 
                "duration": 120,
                "participants": ["Alice", "David", "Eve"],
                "type": "planning",
                "platform": "Google Meet"
            }
        },
        "documents": {
            "doc_1": {
                "meeting_id": "meeting_1",
                "title": "Sprint Goals",
                "content": "Focus on user authentication and database optimization",
                "type": "notes",
                "created_at": "2024-01-15T10:30:00",
                "tags": ["sprint", "goals"]
            }
        },
        "transcripts": {
            "meeting_1": {
                "content": "Alice: Good morning everyone. Let's start with yesterday's progress. Bob: I completed the user login feature. Charlie: I'm working on the database queries.",
                "speakers": ["Alice", "Bob", "Charlie"],
                "language": "en",
                "confidence": 0.95
            }
        }
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        return f.name


async def test_server():
    """Test the server functionality."""
    print("Creating test cache...")
    cache_path = await create_test_cache()
    
    try:
        print(f"Initializing server with cache: {cache_path}")
        server = GranolaMCPServer(cache_path=cache_path)
        
        print("Loading cache...")
        await server._load_cache()
        
        print(f"Loaded {len(server.cache_data.meetings)} meetings")
        print(f"Loaded {len(server.cache_data.documents)} documents")
        print(f"Loaded {len(server.cache_data.transcripts)} transcripts")
        
        # Test search functionality
        print("\nTesting search...")
        results = await server._search_meetings("standup", 5)
        print("Search results:", results[0].text)
        
        # Test meeting details
        print("\nTesting meeting details...")
        details = await server._get_meeting_details("meeting_1")
        print("Meeting details:", details[0].text)
        
        # Test transcript
        print("\nTesting transcript...")
        transcript = await server._get_meeting_transcript("meeting_1")
        print("Transcript:", transcript[0].text[:200] + "...")
        
        # Test pattern analysis
        print("\nTesting pattern analysis...")
        patterns = await server._analyze_meeting_patterns("participants")
        print("Participant patterns:", patterns[0].text)
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        Path(cache_path).unlink()


if __name__ == "__main__":
    asyncio.run(test_server())