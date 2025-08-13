# Granola MCP Server

A Model Context Protocol (MCP) server for integrating Granola.ai meeting intelligence with Claude Desktop.

## Features

- **Meeting Search**: Search meetings by title, content, or participants
- **Meeting Details**: Get comprehensive meeting metadata and information
- **Transcript Access**: Retrieve full meeting transcripts 
- **Document Management**: Access meeting-related documents
- **Pattern Analysis**: Analyze patterns across meetings (participants, frequency, topics)

## Installation

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Configure Claude Desktop by adding to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "granola": {
         "command": "uv",
         "args": ["--directory", "/path/to/granola-ai-mcp", "run", "granola-mcp-server"],
         "env": {}
       }
     }
   }
   ```

## Requirements

- Python 3.12+
- macOS with Granola.ai installed
- Claude Desktop application
- Granola cache file at `~/Library/Application Support/Granola/cache-v3.json`

## Available Tools

### search_meetings
Search meetings by query string.
```
Parameters:
- query (string): Search query for meetings
- limit (integer, optional): Maximum number of results (default: 10)
```

### get_meeting_details  
Get detailed information about a specific meeting.
```
Parameters:
- meeting_id (string): Meeting ID to retrieve details for
```

### get_meeting_transcript
Get transcript for a specific meeting.
```
Parameters:
- meeting_id (string): Meeting ID to get transcript for
```

### get_meeting_documents
Get documents associated with a meeting.
```
Parameters:
- meeting_id (string): Meeting ID to get documents for
```

### analyze_meeting_patterns
Analyze patterns across multiple meetings.
```
Parameters:
- pattern_type (string): Type of pattern to analyze ('topics', 'participants', 'frequency')
- date_range (object, optional): Date range for analysis with start_date and end_date
```

## Usage

Once configured with Claude Desktop, you can use natural language to interact with your Granola meetings:

- "Search for meetings about quarterly planning"
- "Show me details for meeting abc123"  
- "Get the transcript from yesterday's standup"
- "Analyze participant patterns from last month"
- "What documents are associated with the product review meeting?"

## Security

- All data processing happens locally
- No external API calls are made
- Respects existing Granola.ai permissions
- Cache data is parsed from local Granola installation

## Performance

- Lazy loading of transcript data
- Indexed meeting search capabilities  
- Sub-2 second cache loading for hundreds of meetings
- Efficient pattern analysis across large datasets