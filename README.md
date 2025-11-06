# mcp-coded-tools

[![PyPI version](https://badge.fury.io/py/mcp-coded-tools.svg)](https://badge.fury.io/py/mcp-coded-tools)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcp-coded-tools.svg)](https://pypi.org/project/mcp-coded-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/bluman1/mcp-coded-tools/workflows/CI/badge.svg)](https://github.com/bluman1/mcp-coded-tools/actions)

Generate discoverable code from MCP servers for AI agent tool usage.

## Why?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) lets AI agents connect to external tools and data. However, as Anthropic's [engineering post](https://www.anthropic.com/engineering/code-execution-with-mcp) explains, loading hundreds or thousands of tool definitions directly into an agent's context window is inefficient:

- Tool definitions consume excessive tokens (100K+ tokens for large tool sets)
- Intermediate results flow through the context window repeatedly
- Agents become slower and more expensive at scale

**The solution**: Present MCP servers as *code APIs* that agents can discover and use through a filesystem interface. This approach reduces token usage by up to 98.7% while enabling more powerful agent workflows.

**The problem**: Manually writing wrapper code for each MCP tool is tedious.

**mcp-coded-tools**: Automatically generate discoverable Python code from any MCP server.

## Installation

```bash
pip install mcp-coded-tools
```

## Quick Start

### CLI Usage

```bash
# Generate code from popular MCP servers
mcp-coded-tools generate \
  --command "npx -y @modelcontextprotocol/server-github" \
  --output ./servers \
  --server-name github

# Generate from multiple servers for complete workflows
mcp-coded-tools generate \
  --command "npx -y @modelcontextprotocol/server-github" \
  --command "npx -y @modelcontextprotocol/server-postgres" \
  --command "python slack_mcp_server.py" \
  --output ./servers

# Watch mode for development (auto-regenerate on changes)
mcp-coded-tools generate \
  --command "python ./my_mcp_server.py" \
  --output ./tools \
  --watch
```

💡 **See [POPULAR_MCP_SERVERS.md](POPULAR_MCP_SERVERS.md) for 50+ popular servers and real-world use cases!**

💡 **See [WATCH_MODE.md](WATCH_MODE.md) for auto-regeneration during development!**

### Python API

```python
import asyncio
from mcp-coded-tools import MCPCodeGenerator

async def main():
    generator = MCPCodeGenerator()

    # Connect to MCP server and generate code
    await generator.connect_and_scan([
        "npx", "-y", "@modelcontextprotocol/server-gdrive"
    ])

    generator.generate_code(
        output_dir="./servers",
        server_name="google_drive"
    )

    print("✓ Generated discoverable code!")

asyncio.run(main())
```

### What Gets Generated

```
servers/
├── google_drive/
│   ├── __init__.py
│   ├── get_document.py
│   ├── list_files.py
│   └── ...
├── salesforce/
│   ├── __init__.py
│   ├── update_record.py
│   └── ...
└── _client.py
```

Each tool becomes a typed Python function:

```python
# servers/google_drive/get_document.py
from typing import Optional, Dict, Any
from .._client import call_mcp_tool

async def get_document(
    document_id: str,
    fields: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves a document from Google Drive
    """
    return await call_mcp_tool(
        'gdrive_getDocument',
        {'documentId': document_id, 'fields': fields}
    )
```

### Agent Usage

Agents discover tools by exploring the filesystem:

```python
# Agent lists available servers
import os
servers = os.listdir('./servers')
# ['google_drive', 'salesforce', ...]

# Agent reads a specific tool
with open('./servers/google_drive/get_document.py') as f:
    tool_def = f.read()
    # Understands parameters, types, description

# Agent writes code to use tools
import servers.google_drive as gdrive
import servers.salesforce as sf

async def sync_meeting_notes():
    doc = await gdrive.get_document(document_id="abc123")
    
    await sf.update_record(
        object_type="Lead",
        record_id="xyz789",
        data={"Notes": doc['content']}
    )
```

## Features

- ✅ **Automatic code generation** from any MCP server
- ✅ **Type hints** for better IDE support and agent understanding
- ✅ **Docstrings** extracted from MCP tool descriptions
- ✅ **Multiple servers** with automatic namespace separation
- ✅ **CLI and Python API** for flexibility
- ✅ **Error handling** with detailed logging
- ✅ **Async support** for concurrent tool execution

## Configuration

### Server Discovery

By default, tool names are analyzed to extract server prefixes:
- `gdrive_getDocument` → `gdrive` server
- `salesforce_updateRecord` → `salesforce` server

Override with explicit server names:

```python
generator.generate_code(
    output_dir="./servers",
    server_name="my_custom_name"
)
```

### Custom Templates

Customize generated code using Jinja2 templates:

```python
generator = MCPCodeGenerator(
    template_dir="./my_templates"
)
```

## How It Works

1. **Connect**: Establishes connection to MCP server via stdio, HTTP, or SSE
2. **Introspect**: Queries server for all available tools using MCP protocol
3. **Parse**: Extracts tool names, descriptions, and JSON schemas
4. **Generate**: Creates typed Python functions with proper imports
5. **Organize**: Structures code in discoverable filesystem hierarchy

## Use Cases

### 🏢 Enterprise Incident Response

Automate DevOps workflows across multiple systems:

```bash
mcp-coded-tools generate \
  --command "npx -y @modelcontextprotocol/server-postgres" \
  --command "npx -y @modelcontextprotocol/server-github" \
  --command "python slack_mcp_server.py" \
  --output ./devops_tools
```

**Workflow:** Query errors → Create issue → Notify team
**Token Savings:** 98% (150K → 3K tokens)
**Cost Impact:** $3.00 → $0.06 per incident

### 📊 Data Analytics Pipeline

Process millions of rows without context pollution:

```python
from data_tools.postgres import execute_query
from data_tools.slack import post_message

# Query 1M rows - stays in execution environment!
rows = await execute_query(
    query="SELECT * FROM transactions WHERE date > NOW() - INTERVAL '30 days'"
)

# Process data in code (never enters context)
import pandas as pd
df = pd.DataFrame(rows)
summary = df.groupby('user_id')['amount'].sum()

# Only summary goes to context
await post_message(
    channel='analytics',
    text=f"Processed {len(df):,} transactions, total: ${summary.sum():,.2f}"
)
```

**Scale:** Process TBs, not MBs
**ROI:** $109M/year for 500 queries/day operation

### 🤖 Automated Code Review

Review PRs with AI assistance at scale:

```bash
mcp-coded-tools generate \
  --command "npx -y @modelcontextprotocol/server-github" \
  --command "npx -y @modelcontextprotocol/server-filesystem" \
  --command "npx -y @modelcontextprotocol/server-sequential-thinking" \
  --output ./code_review_tools
```

**Impact:** Review 1000s of PRs/day with consistent quality

📚 **See [examples/real_world_workflows.py](examples/real_world_workflows.py) for 5 complete production examples!**

## Development

```bash
# Clone repository
git clone https://github.com/bluman1/mcp-coded-tools.git
cd mcp-coded-tools

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Inspired by Anthropic's [engineering post on code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp).

Built by Michael Ogundare for the MCP community.
