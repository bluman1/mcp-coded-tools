"""
mcp-coded-tools - Generate discoverable code from MCP servers
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import inflection

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from .templates import TemplateRenderer
from .schema_parser import SchemaParser

logger = logging.getLogger(__name__)


class MCPCodeGenerator:
    """
    Generate Python code from MCP server tool definitions.

    This enables AI agents to discover and use MCP tools through a filesystem
    interface, reducing context window usage and improving efficiency.
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the code generator.

        Args:
            template_dir: Optional custom directory for Jinja2 templates
        """
        self.tools: Dict[str, Tool] = {}
        self.template_renderer = TemplateRenderer(template_dir)
        self.schema_parser = SchemaParser()

    async def connect_and_scan(
        self, server_command: List[str], env: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Connect to an MCP server and fetch all tool definitions.

        Args:
            server_command: Command to launch the MCP server (e.g., ["npx", "-y", "server-name"])
            env: Optional environment variables for the server process

        Raises:
            ConnectionError: If unable to connect to the MCP server
            ValueError: If no tools are found on the server
        """
        logger.info(f"Connecting to MCP server: {' '.join(server_command)}")

        try:
            server_params = StdioServerParameters(
                command=server_command[0], args=server_command[1:], env=env
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # List all available tools
                    tools_response = await session.list_tools()

                    if not tools_response.tools:
                        raise ValueError(
                            f"No tools found on MCP server: {' '.join(server_command)}"
                        )

                    # Store tools
                    for tool in tools_response.tools:
                        self.tools[tool.name] = tool
                        logger.debug(f"Discovered tool: {tool.name}")

                    logger.info(f"Successfully scanned {len(tools_response.tools)} tools")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise ConnectionError(f"Could not connect to MCP server: {e}") from e

    def generate_code(
        self,
        output_dir: str = "./servers",
        server_name: Optional[str] = None,
        overwrite: bool = True,
    ) -> Dict[str, List[str]]:
        """
        Generate Python code for all discovered tools.

        Args:
            output_dir: Directory where code will be generated
            server_name: Optional explicit server name (otherwise inferred from tool names)
            overwrite: Whether to overwrite existing files

        Returns:
            Dictionary mapping server names to lists of generated file paths

        Raises:
            ValueError: If no tools have been scanned yet
        """
        if not self.tools:
            raise ValueError("No tools available. Run connect_and_scan() first.")

        logger.info(f"Generating code for {len(self.tools)} tools in {output_dir}")

        base_path = Path(output_dir)
        base_path.mkdir(parents=True, exist_ok=True)

        # Group tools by server
        grouped_tools = self._group_tools(server_name)
        generated_files: Dict[str, List[str]] = {}

        # Generate code for each server
        for server, tools in grouped_tools.items():
            logger.info(f"Generating code for server: {server} ({len(tools)} tools)")

            server_path = base_path / server
            server_path.mkdir(parents=True, exist_ok=True)

            files = []

            # Generate __init__.py
            init_file = self._generate_init(server_path, tools, overwrite)
            if init_file:
                files.append(str(init_file))

            # Generate individual tool files
            for tool_name, tool_def in tools.items():
                tool_file = self._generate_tool_file(server_path, tool_name, tool_def, overwrite)
                if tool_file:
                    files.append(str(tool_file))

            generated_files[server] = files

        # Generate client.py (MCP communication layer)
        client_file = self._generate_client(base_path, overwrite)
        if client_file:
            generated_files["_client"] = [str(client_file)]

        # Generate README for the generated code
        readme_file = self._generate_readme(base_path, grouped_tools, overwrite)
        if readme_file:
            generated_files["_readme"] = [str(readme_file)]

        logger.info(
            f"Code generation complete. Generated {sum(len(f) for f in generated_files.values())} files."
        )

        return generated_files

    def _generate_tool_file(
        self, server_path: Path, tool_name: str, tool_def: Tool, overwrite: bool
    ) -> Optional[Path]:
        """Generate a single tool wrapper file."""
        # Convert tool name to Python function name
        func_name = self._tool_name_to_function(tool_name)
        file_name = f"{func_name}.py"
        file_path = server_path / file_name

        # Check if file exists
        if file_path.exists() and not overwrite:
            logger.warning(f"Skipping {file_path} (already exists)")
            return None

        # Parse schema to get function signature
        parsed_schema = self.schema_parser.parse(tool_def.inputSchema)

        # Generate code from template
        code = self.template_renderer.render_tool(
            func_name=func_name,
            tool_name=tool_def.name,
            description=tool_def.description or "MCP Tool",
            parameters=parsed_schema["parameters"],
            signature=parsed_schema["signature"],
            dict_items=parsed_schema["dict_items"],
        )

        file_path.write_text(code)
        logger.debug(f"Generated: {file_path}")

        return file_path

    def _generate_init(
        self, server_path: Path, tools: Dict[str, Tool], overwrite: bool
    ) -> Optional[Path]:
        """Generate __init__.py that exports all tools."""
        file_path = server_path / "__init__.py"

        if file_path.exists() and not overwrite:
            logger.warning(f"Skipping {file_path} (already exists)")
            return None

        # Get function names for all tools
        function_names = [self._tool_name_to_function(name) for name in tools.keys()]

        code = self.template_renderer.render_init(function_names)
        file_path.write_text(code)
        logger.debug(f"Generated: {file_path}")

        return file_path

    def _generate_client(self, base_path: Path, overwrite: bool) -> Optional[Path]:
        """Generate the core MCP client communication module."""
        file_path = base_path / "_client.py"

        if file_path.exists() and not overwrite:
            logger.warning(f"Skipping {file_path} (already exists)")
            return None

        code = self.template_renderer.render_client()
        file_path.write_text(code)
        logger.debug(f"Generated: {file_path}")

        return file_path

    def _generate_readme(
        self, base_path: Path, grouped_tools: Dict[str, Dict[str, Tool]], overwrite: bool
    ) -> Optional[Path]:
        """Generate README for the generated code."""
        file_path = base_path / "README.md"

        if file_path.exists() and not overwrite:
            logger.warning(f"Skipping {file_path} (already exists)")
            return None

        # Prepare summary data
        servers = []
        for server_name, tools in grouped_tools.items():
            tool_list = [
                {
                    "name": self._tool_name_to_function(name),
                    "description": tool.description or "No description",
                }
                for name, tool in tools.items()
            ]
            servers.append({"name": server_name, "count": len(tools), "tools": tool_list})

        code = self.template_renderer.render_readme(servers)
        file_path.write_text(code)
        logger.debug(f"Generated: {file_path}")

        return file_path

    def _group_tools(self, server_name: Optional[str] = None) -> Dict[str, Dict[str, Tool]]:
        """
        Group tools by server name.

        If server_name is provided, all tools go under that name.
        Otherwise, extract server name from tool prefix (e.g., gdrive_getDocument -> gdrive).
        """
        if server_name:
            return {server_name: self.tools}

        grouped: Dict[str, Dict[str, Tool]] = {}

        for name, tool_def in self.tools.items():
            # Extract server prefix (before first underscore)
            parts = name.split("_")
            server = parts[0] if len(parts) > 1 else "default"

            if server not in grouped:
                grouped[server] = {}

            grouped[server][name] = tool_def

        return grouped

    def _tool_name_to_function(self, tool_name: str) -> str:
        """
        Convert MCP tool name to Python function name.

        Examples:
            gdrive_getDocument -> get_document
            salesforce_updateRecord -> update_record
            listFiles -> list_files
        """
        # Remove server prefix if present
        parts = tool_name.split("_", 1)
        name = parts[1] if len(parts) > 1 else parts[0]

        # Convert to snake_case
        return inflection.underscore(name)

    def list_servers(self) -> List[str]:
        """Get list of server names from discovered tools."""
        grouped = self._group_tools()
        return list(grouped.keys())

    def list_tools(self, server_name: Optional[str] = None) -> List[str]:
        """
        List all discovered tool names.

        Args:
            server_name: Optional server name to filter by

        Returns:
            List of tool names
        """
        if server_name:
            grouped = self._group_tools()
            return list(grouped.get(server_name, {}).keys())

        return list(self.tools.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool information or None if not found
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
            "function_name": self._tool_name_to_function(tool.name),
        }
