#!/usr/bin/env python3
"""Test script that uses the actual Granola cache file."""

import asyncio
import json
import os
from pathlib import Path

from granola_mcp_server.server import GranolaMCPServer


async def test_real_cache():
    """Test the server with real Granola cache if available."""
    cache_path = os.path.expanduser("~/Library/Application Support/Granola/cache-v3.json")
    
    print(f"Looking for Granola cache at: {cache_path}")
    
    # Check if cache file exists
    if not Path(cache_path).exists():
        print("❌ No Granola cache file found")
        print("   This means either:")
        print("   - Granola.ai is not installed")
        print("   - No meetings have been recorded yet")
        print("   - Cache is stored in a different location")
        return False
    
    # Check if cache file is readable
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_size = len(f.read())
        print(f"✅ Cache file found! Size: {cache_size} bytes")
    except PermissionError:
        print("❌ Cache file exists but is not readable (permission denied)")
        return False
    except Exception as e:
        print(f"❌ Error reading cache file: {e}")
        return False
    
    try:
        print("\n" + "="*60)
        print("TESTING WITH REAL GRANOLA CACHE")
        print("="*60)
        
        # Initialize server with real cache
        server = GranolaMCPServer(cache_path=cache_path)
        
        print("Loading real cache data...")
        await server._load_cache()
        
        if not server.cache_data:
            print("❌ Failed to load cache data")
            return False
        
        # Show what we loaded
        meeting_count = len(server.cache_data.meetings)
        doc_count = len(server.cache_data.documents)
        transcript_count = len(server.cache_data.transcripts)
        
        print(f"✅ Successfully loaded real cache data:")
        print(f"   📅 {meeting_count} meetings")
        print(f"   📄 {doc_count} documents")
        print(f"   🗣️ {transcript_count} transcripts")
        
        if meeting_count == 0:
            print("\n⚠️  No meetings found in cache - Granola may not have processed any meetings yet")
            return True
        
        print(f"\n📊 CACHE ANALYSIS:")
        if server.cache_data.last_updated:
            print(f"   Last updated: {server.cache_data.last_updated}")
        
        # Show sample meeting titles
        sample_meetings = list(server.cache_data.meetings.values())[:3]
        if sample_meetings:
            print(f"\n📅 SAMPLE MEETINGS:")
            for i, meeting in enumerate(sample_meetings, 1):
                print(f"   {i}. {meeting.title}")
                print(f"      Date: {meeting.date.strftime('%Y-%m-%d %H:%M')}")
                if meeting.participants:
                    print(f"      Participants: {', '.join(meeting.participants)}")
                print()
        
        print("="*60)
        print("TESTING SERVER FUNCTIONALITY WITH REAL DATA")
        print("="*60)
        
        # Test search functionality
        print("\n🔍 Testing search with 'meeting'...")
        results = await server._search_meetings("meeting", 3)
        print("Search results:", results[0].text[:200] + "..." if results[0].text else "No results")
        
        # Test getting details of first meeting
        if sample_meetings:
            first_meeting_id = sample_meetings[0].id
            print(f"\n📋 Testing meeting details for ID: {first_meeting_id}...")
            details = await server._get_meeting_details(first_meeting_id)
            print("Meeting details:", details[0].text[:300] + "..." if details[0].text else "No details")
            
            # Test transcript if available
            if first_meeting_id in server.cache_data.transcripts:
                print(f"\n🗣️ Testing transcript for meeting: {first_meeting_id}...")
                transcript = await server._get_meeting_transcript(first_meeting_id)
                print("Transcript preview:", transcript[0].text[:200] + "..." if transcript[0].text else "No transcript")
        
        # Validate document panel content when present
        try:
            with open(cache_path, 'r', encoding='utf-8') as cache_file:
                cache_json = json.load(cache_file)
            state = json.loads(cache_json.get('cache', '{}')).get('state', {})
        except Exception as exc:
            print(f"\n⚠️ Unable to parse raw cache for panel validation: {exc}")
            state = {}

        panels = state.get('documentPanels', {})
        meetings_meta = state.get('meetingsMetadata', {})

        checked = skipped = failures = 0
        recent_meetings = sorted(
            meetings_meta.items(),
            key=lambda item: item[1].get('created_at', ''),
            reverse=True
        )[:10]

        for meeting_id, _meta in recent_meetings:
            panel_data = panels.get(meeting_id)
            if not panel_data:
                skipped += 1
                continue

            if meeting_id not in server.cache_data.documents:
                skipped += 1
                continue

            docs = await server._get_meeting_documents(meeting_id)
            document_text = docs[0].text if docs else ''

            if document_text and document_text.strip():
                checked += 1
            else:
                print(f"\n❌ Panel-backed meeting '{meeting_id}' produced empty document content")
                failures += 1

        print(f"\n📄 Panel validation summary: checked={checked}, skipped={skipped}, failures={failures}")

        if failures:
            raise AssertionError("Some meetings with document panels yielded empty content")

        # Test pattern analysis
        print(f"\n📊 Testing participant pattern analysis...")
        patterns = await server._analyze_meeting_patterns("participants")
        print("Pattern analysis:", patterns[0].text[:300] + "..." if patterns[0].text else "No patterns")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED WITH REAL GRANOLA DATA!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧪 GRANOLA MCP SERVER - REAL CACHE TEST")
    print("="*60)
    
    success = await test_real_cache()
    
    if success:
        print("\n🎉 SUCCESS: Server works perfectly with real Granola data!")
    else:
        print("\n⚠️  Note: Server will still work fine, just with empty data")
        print("   To get real meeting data:")
        print("   1. Install Granola.ai")
        print("   2. Record some meetings")
        print("   3. Run this test again")


if __name__ == "__main__":
    asyncio.run(main())