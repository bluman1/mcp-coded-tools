# Quick Start Guide

Get up and running with mcp-coded-tools in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Node.js (for MCP servers via npm)

## Installation

```bash
pip install mcp-coded-tools
```

## 1. Generate Code (CLI)

The fastest way to get started:

```bash
# Generate from Google Drive MCP server
mcp-coded-tools generate \
  --command "npx -y @modelcontextprotocol/server-gdrive" \
  --output ./servers

# That's it! Code is now in ./servers/
```

## 2. Generate Code (Python)

Or use the Python API:

```python
import asyncio
from mcp-coded-tools import MCPCodeGenerator

async def main():
    generator = MCPCodeGenerator()
    
    # Connect and scan
    await generator.connect_and_scan([
        "npx", "-y", "@modelcontextprotocol/server-gdrive"
    ])
    
    # Generate code
    generator.generate_code(output_dir="./servers")

asyncio.run(main())
```

## 3. Use Generated Tools

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-gdrive"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Initialize generated MCP client
            from servers._client import set_session
            set_session(session)
            
            # Use generated tools!
            from servers.gdrive import list_files
            
            files = await list_files(folder_id="root", max_results=10)
            print(f"Found {len(files)} files")

asyncio.run(main())
```

## Common Use Cases

### Multiple Servers

```bash
mcp-coded-tools generate \
  -c "npx -y @modelcontextprotocol/server-gdrive" \
  -c "npx -y @modelcontextprotocol/server-slack" \
  -o ./servers
```

### Custom Server Name

```bash
mcp-coded-tools generate \
  -c "python my_mcp_server.py" \
  -s my_tools \
  -o ./servers
```

### Inspect Before Generating

```bash
# See what tools are available
mcp-coded-tools inspect -c "npx -y @modelcontextprotocol/server-gdrive"
```

### Initialize New Project

```bash
# Create project structure
mcp-coded-tools init ./my-agent-project
cd my-agent-project

# Generate tools
mcp-coded-tools generate -c "your-mcp-server" -o ./servers

# Run agent
python agent.py
```

## Project Structure

After generation, you'll have:

```
servers/
├── google_drive/           # Server namespace
│   ├── __init__.py        # Exports all tools
│   ├── get_document.py    # Individual tool
│   ├── list_files.py
│   └── ...
├── _client.py             # MCP communication layer
└── README.md              # Generated documentation
```

## What Gets Generated

Each tool becomes a typed Python function:

```python
# servers/google_drive/get_document.py
async def get_document(
    document_id: str,
    fields: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves a document from Google Drive
    
    Args:
        document_id (required): The ID of the document
        fields (optional): Specific fields to return
    """
    return await call_mcp_tool(
        'gdrive_getDocument',
        {'documentId': document_id, 'fields': fields}
    )
```

## Next Steps

1. Check out [examples/](examples/) for more detailed usage
2. Read the [full README](README.md) for comprehensive documentation
3. See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
4. Read Anthropic's [blog post](https://www.anthropic.com/engineering/code-execution-with-mcp) on why this pattern is powerful

## Troubleshooting

**Error: "MCP session not initialized"**
- Make sure you call `set_session(session)` before using tools

**Error: "No module named 'servers'"**
- Run `mcp-coded-tools generate` first to create the code
- Make sure you're in the right directory

**Error: "Connection failed"**
- Verify the MCP server command is correct
- Check that required dependencies are installed (e.g., npm packages)

**Import errors in generated code**
- Make sure `mcp` is installed: `pip install mcp`

## Support

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/bluman1/mcp-coded-tools/issues)
- 💬 [Discussions](https://github.com/bluman1/mcp-coded-tools/discussions)
- 📧 [Email](mailto:hey@michael.ng)
