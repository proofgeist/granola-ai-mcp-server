# GranolaAI MCP Server

An experimental Model Context Protocol (MCP) server for integrating Granola.ai meeting intelligence with Claude Desktop. This uses Granola's local cache. I don't have any idea how Granola updates or maintains that cache. My guess is that it's doing a rolling context window, but storing long term notes up in AWS. So, YMMV. Use at your own risk. I will likely add a cache shipper at some point since we don't have access to Gronala's data in the cloud.

## Features

- **Meeting Search**: Search meetings by title, content, participants, and transcript content
- **Meeting Details**: Get comprehensive meeting metadata with local timezone display
- **Full Transcript Access**: Retrieve complete meeting conversations with speaker identification
- **Rich Document Content**: Access actual meeting notes, summaries, and structured content
- **Pattern Analysis**: Analyze patterns across meetings (participants, frequency, topics)
- **Timezone Intelligence**: All timestamps automatically display in your local timezone
- **Real-time Integration**: Seamlessly connects to your actual Granola meeting data

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- macOS with Granola.ai installed
- Granola cache file at `~/Library/Application Support/Granola/cache-v3.json`

### One-Click Install for Cursor (Recommended)

[![Add Granola MCP to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=granola&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL3Byb29mZ2Vpc3QvZ3Jhbm9sYS1haS1tY3Atc2VydmVyIiwiZ3Jhbm9sYS1tY3Atc2VydmVyIl0sImVudiI6e319)

Click the button above to automatically add the Granola MCP server to Cursor.

> **Note:** This requires [uv](https://docs.astral.sh/uv/) to be installed and Granola.ai to be running on macOS.

### Manual Installation (Claude Desktop)

<details>
<summary>Click to expand manual setup instructions</summary>

1. **Clone the repository to your home directory:**
   ```bash
   cd ~
   git clone https://github.com/proofgeist/granola-ai-mcp-server
   cd granola-ai-mcp-server
   ```
   
   **Important:** Clone to your home directory (`~`) rather than `~/Documents` to avoid macOS permission issues with Claude Desktop.

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
         "command": "/Users/YOUR_USERNAME/granola-ai-mcp-server/.venv/bin/granola-mcp-server",
         "args": [],
         "env": {}
       }
     }
   }
   ```
   
   **Important:** 
   - Replace `YOUR_USERNAME` with your actual macOS username
   - Use the direct path to the virtual environment's script (not `uv run`) to avoid working directory issues
   - The path should point to your home directory installation

5. **Restart Claude Desktop** to load the MCP server:
   ```bash
   # Quit Claude completely
   osascript -e 'quit app "Claude"'
   # Reopen Claude
   open -a "Claude"
   ```

</details>

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

### Basic Queries
- "Search for meetings about quarterly planning"
- "Show me yesterday's meetings"
- "Find meetings with David from this week"

### Transcript Access
- "Get the transcript from yesterday's ProofChat meeting"
- "What was discussed in the Float rollback planning meeting?"
- "Show me the full conversation from the David Tibbi meeting"

### Content Analysis
- "Analyze participant patterns from last month"
- "What documents are associated with the product review meeting?"
- "Search for mentions of 'schema labeling' in meeting transcripts"

### Recent Meeting Intelligence
The server automatically detects and provides access to:
- **Full transcripts** from recent meetings (25,000+ characters)
- **Meeting content** including notes and summaries
- **Participant information** and speaker identification
- **Local timezone display** for all meeting times

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

## Performance & Capabilities

- **Fast Loading**: Sub-2 second cache loading for hundreds of meetings
- **Rich Content**: Extracts 25,000+ character transcripts and meeting notes
- **Efficient Search**: Multi-field search across titles, content, participants, and transcripts
- **Memory Optimized**: Lazy loading with intelligent content parsing
- **Timezone Smart**: Automatic local timezone detection and display
- **Production Ready**: Successfully processes real Granola data (11.7MB cache files)
- **Scalable**: Handles large datasets with 500+ transcript segments per meeting

## Current Status

🚀 **PRODUCTION READY** - Successfully tested with real Granola.ai data including:
- ✅ **39+ meetings** parsed and searchable
- ✅ **28 full transcripts** with complete conversations  
- ✅ **Rich meeting content** from notes, summaries, and structured data
- ✅ **Timezone intelligence** showing times like "17:04" instead of "21:04 UTC"
- ✅ **Speaker identification** and conversation flow
- ✅ **Yesterday's meetings** fully accessible with detailed content

## Troubleshooting

### Common Issues

**"Cache file not found"**
- Ensure Granola.ai is installed and has processed some meetings
- Check that the cache file exists: `ls -la "~/Library/Application Support/Granola/cache-v3.json"`

**"uv command not found"**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or use pip fallback in Claude config: `"command": "python"`

**"Permission denied" or "Operation not permitted"**
- **Most common issue on macOS**: This happens when the server is installed in `~/Documents` or other protected folders
- **Solution 1 (Recommended)**: Move the installation to your home directory:
  ```bash
  mv ~/Documents/granola-ai-mcp-server ~/granola-ai-mcp-server
  cd ~/granola-ai-mcp-server
  uv sync  # Rebuild venv with correct paths
  ```
  Then update the path in `claude_desktop_config.json`

- **Solution 2**: Grant Claude Desktop Full Disk Access:
  1. Open System Settings → Privacy & Security → Full Disk Access
  2. Click the lock icon and authenticate
  3. Click "+" and add `/Applications/Claude.app`
  4. Toggle Claude to "On"
  5. Restart Claude Desktop

**"Current directory does not exist"**
- This error occurs when using `uv run` with the `--directory` flag
- Use the direct path to the venv script instead (see Installation step 4)

**Server not appearing in Claude Desktop**
- Verify the absolute path in your Claude config
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp-server-granola.log`
- Look for Python errors in the logs
- Ensure the path doesn't contain spaces or special characters
- Restart Claude Desktop after config changes

**"Failed to spawn process" or "No such file or directory"**
- The Python shebang in the venv script points to the wrong location
- Run `uv sync` in the project directory to rebuild the venv
- Verify the script exists: `ls -la ~/granola-ai-mcp-server/.venv/bin/granola-mcp-server`

### Meeting notes appear empty in Claude
- Granola sometimes stores rich notes inside `documentPanels` rather than `notes_plain`
- This server now reads those panels by default; set `GRANOLA_PARSE_PANELS=0` in the environment to disable
- Run `python test_real_cache.py` to verify that panel-backed notes produce content
