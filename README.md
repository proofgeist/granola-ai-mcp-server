# Granola MCP Server

A Model Context Protocol (MCP) server for integrating Granola.ai meeting intelligence with Claude Desktop.

## Features

- **Meeting Search**: Search meetings by title, content, or participants
- **Meeting Details**: Get comprehensive meeting metadata and information
- **Transcript Access**: Retrieve full meeting transcripts 
- **Document Management**: Access meeting-related documents
- **Pattern Analysis**: Analyze patterns across meetings (participants, frequency, topics)

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- macOS with Granola.ai installed
- Claude Desktop application
- Granola cache file at `~/Library/Application Support/Granola/cache-v3.json`

### Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd granola-ai-mcp
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Test the installation:**
   ```bash
   uv run python test_server.py
   ```

4. **Configure Claude Desktop** by adding to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "granola": {
         "command": "uv",
         "args": ["--directory", "/absolute/path/to/granola-ai-mcp", "run", "granola-mcp-server"],
         "env": {}
       }
     }
   }
   ```
   
   **Important:** Replace `/absolute/path/to/granola-ai-mcp` with your actual project path.

5. **Restart Claude Desktop** to load the MCP server

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

## Usage Examples

Once configured with Claude Desktop, you can use natural language to interact with your Granola meetings:

- "Search for meetings about quarterly planning"
- "Show me details for meeting abc123"  
- "Get the transcript from yesterday's standup"
- "Analyze participant patterns from last month"
- "What documents are associated with the product review meeting?"

## Development

### Running Tests
```bash
uv run python test_server.py
```

### Running the Server Directly
```bash
uv run granola-mcp-server
```

### Adding Dependencies
```bash
uv add package-name
```

## Configuration

### Claude Desktop Config Locations
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Granola Cache Location
The server reads from Granola's cache file at:
```
~/Library/Application Support/Granola/cache-v3.json
```

## Security & Privacy

- ✅ **100% Local Processing** - All data stays on your machine
- ✅ **No External API Calls** - No data sent to external services
- ✅ **Granola Permissions Respected** - Uses existing Granola.ai access controls
- ✅ **Read-Only Access** - Server only reads from Granola's cache

## Performance

- **Fast Loading**: Sub-2 second cache loading for hundreds of meetings
- **Efficient Search**: Multi-field search with relevance scoring
- **Memory Optimized**: Lazy loading of transcript data
- **Scalable**: Handles large datasets with efficient pattern analysis

## Troubleshooting

### Common Issues

**"Cache file not found"**
- Ensure Granola.ai is installed and has processed some meetings
- Check that the cache file exists: `ls -la "~/Library/Application Support/Granola/cache-v3.json"`

**"uv command not found"**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or use pip fallback in Claude config: `"command": "python"`

**"Permission denied"**
- Ensure the cache file is readable: `chmod 644 "~/Library/Application Support/Granola/cache-v3.json"`

**Server not appearing in Claude Desktop**
- Verify the absolute path in your Claude config
- Check Claude Desktop logs for MCP server errors
- Restart Claude Desktop after config changes