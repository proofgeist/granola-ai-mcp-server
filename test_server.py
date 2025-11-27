#!/usr/bin/env python3
"""Enhanced test script for Granola MCP Server."""

import asyncio
import json
import tempfile
from pathlib import Path

from granola_mcp_server.server import GranolaMCPServer


async def create_test_cache_with_panels():
    """Create a synthetic cache that exercises panel parsing."""
    state = {
        "meetingsMetadata": {
            "m1": {
                "created_at": "2024-01-15T10:00:00",
                "title": "Service Review"
            },
            "m2": {
                "created_at": "2024-01-16T11:00:00",
                "title": "Retro"
            }
        },
        "documents": {
            "m1": {
                "title": "Service Review",
                "created_at": "2024-01-15T10:05:00",
                "notes_plain": "",
                "notes_markdown": "",
                "notes": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": []
                        }
                    ]
                }
            },
            "m2": {
                "title": "Retro",
                "created_at": "2024-01-16T11:05:00",
                "notes_plain": "Direct notes",
                "notes_markdown": "",
                "notes": {
                    "type": "doc",
                    "content": []
                }
            }
        },
        "documentPanels": {
            "m1": {
                "panel-1": {
                    "content": [
                        {
                            "type": "heading",
                            "content": [
                                {"type": "text", "text": "Service Review"}
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Hello Panel"}
                            ]
                        }
                    ]
                }
            }
        },
        "transcripts": {}
    }

    cache_wrapper = {"cache": json.dumps({"state": state})}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
        json.dump(cache_wrapper, handle)
        return handle.name


async def test_server():
    """Test the server functionality with panel and plain notes."""
    print("Creating synthetic test cache...")
    cache_path = await create_test_cache_with_panels()

    try:
        print(f"Initializing server with cache: {cache_path}")
        server = GranolaMCPServer(cache_path=cache_path)

        print("Loading cache...")
        await server._load_cache()

        assert server.cache_data, "Cache data should not be empty"
        assert "m1" in server.cache_data.documents, "Document m1 should be parsed"
        assert "m2" in server.cache_data.documents, "Document m2 should be parsed"

        m1_content = server.cache_data.documents["m1"].content
        m2_content = server.cache_data.documents["m2"].content

        assert "Hello Panel" in m1_content, "Panel text should be extracted for m1"
        assert "Direct notes" in m2_content, "notes_plain should take precedence for m2"

        print("Synthetic content checks passed.")

        # Minimal smoke for existing flows
        await server._search_meetings("Service", 5)
        await server._get_meeting_documents("m1")

        print("\n✅ Panel fallback test passed!")

    except Exception as exc:
        print(f"❌ Test failed: {exc}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        Path(cache_path).unlink()


if __name__ == "__main__":
    asyncio.run(test_server())