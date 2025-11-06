"""
Command-line interface for mcp-coded-tools
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .generator import MCPCodeGenerator


# Configure logging
def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


@click.group()
@click.version_option()
def cli() -> None:
    """
    mcp-coded-tools - Generate discoverable code from MCP servers

    Generate Python code from MCP tool definitions to enable efficient
    agent tool discovery through filesystem interfaces.
    """
    pass


@cli.command()
@click.option(
    "--command",
    "-c",
    "commands",
    multiple=True,
    required=True,
    help='MCP server command (can be specified multiple times). Example: -c "npx -y @modelcontextprotocol/server-gdrive"',
)
@click.option(
    "--output",
    "-o",
    default="./servers",
    help="Output directory for generated code (default: ./servers)",
    type=click.Path(),
)
@click.option(
    "--server-name", "-s", help="Explicit server name (otherwise inferred from tool names)"
)
@click.option(
    "--overwrite/--no-overwrite", default=True, help="Overwrite existing files (default: true)"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--template-dir",
    "-t",
    help="Custom template directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--watch", "-w", is_flag=True, help="Watch server files for changes and auto-regenerate"
)
def generate(
    commands: Tuple[str, ...],
    output: str,
    server_name: Optional[str],
    overwrite: bool,
    verbose: bool,
    template_dir: Optional[str],
    watch: bool,
) -> None:
    """
    Generate code from MCP server(s).

    Examples:

        # Generate from a single server
        mcp-coded-tools generate -c "npx -y @modelcontextprotocol/server-gdrive" -o ./servers

        # Generate from multiple servers
        mcp-coded-tools generate \\
            -c "npx -y @modelcontextprotocol/server-gdrive" \\
            -c "python salesforce_server.py" \\
            -o ./servers

        # Use explicit server name
        mcp-coded-tools generate -c "python my_server.py" -s my_custom_name

        # Watch for changes and auto-regenerate
        mcp-coded-tools generate -c "python my_server.py" -o ./servers --watch
    """
    setup_logging(verbose)

    click.echo("🔨 mcp-coded-tools - Generating code from MCP servers")
    click.echo()

    # Run async generation
    asyncio.run(
        _async_generate(
            commands=commands,
            output=output,
            server_name=server_name,
            overwrite=overwrite,
            template_dir=template_dir,
            watch=watch,
        )
    )


async def _async_generate(
    commands: Tuple[str, ...],
    output: str,
    server_name: Optional[str],
    overwrite: bool,
    template_dir: Optional[str],
    watch: bool = False,
) -> None:
    """Async implementation of generate command."""

    async def do_generation() -> None:
        """Perform the actual generation."""
        try:
            generator = MCPCodeGenerator(template_dir=template_dir)

            # Scan all specified servers
            for cmd in commands:
                # Parse command string into list
                cmd_parts = cmd.split()

                click.echo(f"📡 Connecting to MCP server: {cmd}")
                await generator.connect_and_scan(cmd_parts)

            # Generate code
            click.echo(f"✍️  Generating code in {output}...")
            generated_files = generator.generate_code(
                output_dir=output, server_name=server_name, overwrite=overwrite
            )

            # Display summary
            total_files = sum(len(files) for files in generated_files.values())
            click.echo()
            click.echo(f"✅ Success! Generated {total_files} files:")
            click.echo()

            for server, files in generated_files.items():
                if server.startswith("_"):
                    continue  # Skip meta files
                click.echo(f"  📦 {server}:")
                for file_path in files[:5]:  # Show first 5 files
                    click.echo(f"     - {file_path}")
                if len(files) > 5:
                    click.echo(f"     ... and {len(files) - 5} more")

            click.echo()
            click.echo(f"📁 All code generated in: {output}")

            if not watch:
                click.echo()
                click.echo("💡 Next steps:")
                click.echo(f"   1. Review the generated code in {output}/")
                click.echo("   2. Initialize MCP session in your agent runtime")
                click.echo(f"   3. Import and use: import {Path(output).name}.server_name")

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            if logging.getLogger().level == logging.DEBUG:
                raise
            if not watch:
                sys.exit(1)

    # Initial generation
    await do_generation()

    # If watch mode, set up file monitoring
    if watch:
        click.echo()
        click.echo("👀 Watching for changes... (Press Ctrl+C to stop)")
        click.echo()

        # Extract file paths to watch from commands
        watch_paths = []
        for cmd in commands:
            cmd_parts = cmd.split()
            # If command is python/node with a file, watch that file
            if len(cmd_parts) >= 2 and cmd_parts[0] in ["python", "python3", "node"]:
                file_path = Path(cmd_parts[1])
                if file_path.exists() and file_path.is_file():
                    watch_paths.append(file_path.parent)
                    click.echo(f"   Watching: {file_path}")

        if not watch_paths:
            click.echo("   ⚠️  No local files detected in commands")
            click.echo("   Watch mode works best with local MCP servers")
            click.echo("   Example: -c 'python ./my_server.py'")
            return

        # Set up file watcher
        class RegenerateHandler(FileSystemEventHandler):
            def __init__(self) -> None:
                self.last_regeneration: float = 0.0
                self.debounce_seconds: int = 2  # Wait 2 seconds between regenerations

            def on_modified(self, event: FileSystemEvent) -> None:
                # Only watch .py files
                if not isinstance(event.src_path, str) or not event.src_path.endswith(".py"):
                    return

                # Debounce rapid file changes
                now = time.time()
                if now - self.last_regeneration < self.debounce_seconds:
                    return

                self.last_regeneration = now

                click.echo()
                src_path_str = (
                    event.src_path if isinstance(event.src_path, str) else str(event.src_path)
                )
                click.echo(f"🔄 Change detected: {Path(src_path_str).name}")
                click.echo(f"   {datetime.now().strftime('%H:%M:%S')} - Regenerating...")
                click.echo()

                # Regenerate (run in sync context)
                try:
                    asyncio.run(do_generation())
                except Exception as e:
                    click.echo(f"❌ Regeneration failed: {e}")
                    click.echo()

        # Start observer
        observer = Observer()
        handler = RegenerateHandler()

        for path in watch_paths:
            observer.schedule(handler, str(path), recursive=True)

        observer.start()

        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            click.echo()
            click.echo("👋 Stopping watch mode...")
            observer.stop()
            observer.join()


@cli.command()
@click.option(
    "--command",
    "-c",
    required=True,
    help='MCP server command. Example: "npx -y @modelcontextprotocol/server-gdrive"',
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def inspect(command: str, verbose: bool) -> None:
    """
    Inspect an MCP server to see available tools without generating code.

    Example:
        mcp-coded-tools inspect -c "npx -y @modelcontextprotocol/server-gdrive"
    """
    setup_logging(verbose)

    click.echo(f"🔍 Inspecting MCP server: {command}")
    click.echo()

    asyncio.run(_async_inspect(command))


async def _async_inspect(command: str) -> None:
    """Async implementation of inspect command."""
    try:
        generator = MCPCodeGenerator()

        # Parse command string
        cmd_parts = command.split()

        # Scan server
        await generator.connect_and_scan(cmd_parts)

        # Display tools
        servers = generator.list_servers()

        click.echo(f"📦 Found {len(servers)} server(s):")
        click.echo()

        for server in servers:
            tools = generator.list_tools(server)
            click.echo(f"  {server} ({len(tools)} tools):")

            for tool_name in tools:
                info = generator.get_tool_info(tool_name)
                if info:
                    desc = info["description"] or "No description"
                    # Truncate long descriptions
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    click.echo(f"    • {info['function_name']}: {desc}")

            click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if logging.getLogger().level == logging.DEBUG:
            raise
        sys.exit(1)


@cli.command()
@click.argument("output_dir", type=click.Path())
def init(output_dir: str) -> None:
    """
    Initialize a new project structure for agent code.

    Creates a starter template with example MCP integration.

    Example:
        mcp-coded-tools init ./my-agent-project
    """
    output_path = Path(output_dir)

    click.echo(f"🚀 Initializing agent project in {output_dir}")

    # Create directory structure
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "servers").mkdir(exist_ok=True)

    # Create example agent file
    agent_example = '''"""
Example agent using generated MCP tools
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import generated tools (after running mcp-coded-tools generate)
# from servers.google_drive import get_document
# from servers.salesforce import update_record


async def main():
    """Example agent workflow."""
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-gdrive"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Initialize MCP client for generated tools
            from servers._client import set_session
            set_session(session)
            
            # Now use generated tools
            # doc = await get_document(document_id="abc123")
            # print(f"Document: {doc}")
            
            print("Agent initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
'''

    (output_path / "agent.py").write_text(agent_example)

    # Create README
    readme = f"""# Agent Project

This project uses mcp-coded-tools to generate discoverable tools from MCP servers.

## Setup

1. Install dependencies:
```bash
pip install mcp-coded-tools
```

2. Generate tools from MCP servers:
```bash
mcp-coded-tools generate -c "npx -y @modelcontextprotocol/server-gdrive" -o ./servers
```

3. Run the agent:
```bash
python agent.py
```

## Structure

```
{output_dir}/
├── agent.py           # Your agent code
├── servers/           # Generated MCP tools
│   ├── google_drive/
│   ├── _client.py
│   └── README.md
└── README.md          # This file
```

## Next Steps

1. Modify agent.py to implement your agent logic
2. Use generated tools from servers/ directory
3. Add more MCP servers as needed
"""

    (output_path / "README.md").write_text(readme)

    click.echo("✅ Project initialized!")
    click.echo()
    click.echo("📁 Created:")
    click.echo(f"   {output_dir}/agent.py")
    click.echo(f"   {output_dir}/servers/")
    click.echo(f"   {output_dir}/README.md")
    click.echo()
    click.echo("💡 Next steps:")
    click.echo(f"   1. cd {output_dir}")
    click.echo('   2. mcp-coded-tools generate -c "your-mcp-server" -o ./servers')
    click.echo("   3. python agent.py")


def main() -> None:
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
