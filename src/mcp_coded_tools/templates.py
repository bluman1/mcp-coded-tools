"""
Template rendering for code generation
"""

from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    """
    Render code templates using Jinja2.
    """

    def __init__(self, template_dir: Optional[str] = None) -> None:
        """
        Initialize template renderer.

        Args:
            template_dir: Optional custom template directory.
                         If None, uses built-in templates.
        """
        if template_dir:
            self.env: Optional[Environment] = Environment(
                loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
            )
        else:
            # Use built-in templates
            self.env = None

    def render_tool(
        self,
        func_name: str,
        tool_name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        signature: str,
        dict_items: str,
    ) -> str:
        """Render a tool function file."""
        if self.env:
            template = self.env.get_template("tool.py.j2")
            return template.render(
                func_name=func_name,
                tool_name=tool_name,
                description=description,
                parameters=parameters,
                signature=signature,
                dict_items=dict_items,
            )

        # Built-in template
        return self._builtin_tool_template(
            func_name=func_name,
            tool_name=tool_name,
            description=description,
            parameters=parameters,
            signature=signature,
            dict_items=dict_items,
        )

    def render_init(self, function_names: List[str]) -> str:
        """Render __init__.py file."""
        if self.env:
            template = self.env.get_template("__init__.py.j2")
            return template.render(function_names=function_names)

        # Built-in template
        return self._builtin_init_template(function_names)

    def render_client(self) -> str:
        """Render the MCP client module."""
        if self.env:
            template = self.env.get_template("_client.py.j2")
            return template.render()

        # Built-in template
        return self._builtin_client_template()

    def render_readme(self, servers: List[Dict[str, Any]]) -> str:
        """Render README.md for generated code."""
        if self.env:
            template = self.env.get_template("README.md.j2")
            return template.render(servers=servers)

        # Built-in template
        return self._builtin_readme_template(servers)

    # Built-in templates

    def _builtin_tool_template(
        self,
        func_name: str,
        tool_name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        signature: str,
        dict_items: str,
    ) -> str:
        """Built-in template for tool functions."""
        # Determine which typing imports we need
        typing_imports = {"Any", "Dict"}
        has_optional = any(not p["required"] for p in parameters)
        if has_optional:
            typing_imports.add("Optional")

        # Check for List, Union, Literal in types
        for param in parameters:
            if "List[" in param["type"]:
                typing_imports.add("List")
            if "Union[" in param["type"]:
                typing_imports.add("Union")
            if "Literal[" in param["type"]:
                typing_imports.add("Literal")

        imports = ", ".join(sorted(typing_imports))

        # Format description as docstring
        doc_lines = [description]
        if parameters:
            doc_lines.append("")
            doc_lines.append("Args:")
            for param in parameters:
                req_marker = "required" if param["required"] else "optional"
                param_doc = f"    {param['name']} ({req_marker}): {param['description'] or 'No description'}"
                doc_lines.append(param_doc)

        docstring = "\n    ".join(doc_lines)

        return f'''"""
Generated MCP tool wrapper
"""
from typing import {imports}
from .._client import call_mcp_tool


async def {func_name}({signature}) -> Dict[str, Any]:
    """
    {docstring}
    """
    return await call_mcp_tool(
        '{tool_name}',
        {{{dict_items}}}
    )
'''

    def _builtin_init_template(self, function_names: List[str]) -> str:
        """Built-in template for __init__.py."""
        imports = "\n".join(f"from .{name} import {name}" for name in sorted(function_names))

        all_exports = ", ".join(f'"{name}"' for name in sorted(function_names))

        return f'''"""
Generated MCP server tools
"""
{imports}

__all__ = [{all_exports}]
'''

    def _builtin_client_template(self) -> str:
        """Built-in template for MCP client."""
        return '''"""
Core MCP client for tool execution

This module handles communication with the MCP server.
It should be initialized by your agent runtime.
"""
from mcp import ClientSession
from typing import Any, Dict, Optional

# Global session - initialized by the agent harness
_session: Optional[ClientSession] = None


def set_session(session: ClientSession) -> None:
    """
    Initialize the MCP client session.
    
    This should be called once at startup by your agent runtime.
    
    Args:
        session: Active MCP ClientSession
    """
    global _session
    _session = session


def get_session() -> Optional[ClientSession]:
    """Get the current MCP session."""
    return _session


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Execute an MCP tool call.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments as a dictionary
        
    Returns:
        Tool result
        
    Raises:
        RuntimeError: If MCP session not initialized
        Exception: If tool call fails
    """
    if _session is None:
        raise RuntimeError(
            "MCP session not initialized. Call set_session() first."
        )
    
    try:
        result = await _session.call_tool(tool_name, arguments)
        
        # Extract content from result
        if hasattr(result, 'content'):
            # MCP returns CallToolResult with content array
            if result.content:
                # Return first content item's data
                first_content = result.content[0]
                if hasattr(first_content, 'text'):
                    return first_content.text
                return first_content
            return None
        
        return result
        
    except Exception as e:
        raise Exception(f"MCP tool call failed for {tool_name}: {e}") from e
'''

    def _builtin_readme_template(self, servers: List[Dict[str, Any]]) -> str:
        """Built-in template for README."""
        sections = []

        sections.append(
            """# Generated MCP Tools

This directory contains auto-generated code from MCP servers.
Generated by [mcp-coded-tools](https://github.com/bluman1/mcp-coded-tools).

## Usage

```python
# Initialize MCP session (done by agent runtime)
from servers._client import set_session
set_session(your_mcp_session)

# Use generated tools
import servers.google_drive as gdrive

async def example():
    doc = await gdrive.get_document(document_id="abc123")
    print(doc)
```

## Available Servers
"""
        )

        for server in servers:
            sections.append(f"\n### {server['name']} ({server['count']} tools)\n")
            for tool in server["tools"]:
                sections.append(f"- `{tool['name']}`: {tool['description']}")

        sections.append(
            """
## Regenerating Code

To regenerate this code after MCP server updates:

```bash
mcp-coded-tools generate --command "your-server-command" --output ./servers
```

## Structure

```
servers/
├── server_name/
│   ├── __init__.py        # Exports all tools
│   ├── tool_one.py        # Individual tool wrapper
│   └── tool_two.py
├── _client.py             # MCP communication layer
└── README.md              # This file
```
"""
        )

        return "\n".join(sections)
