"""
mcp-coded-tools - Generate discoverable code from MCP servers

This package generates Python code from MCP tool definitions to enable
efficient AI agent tool discovery through filesystem interfaces.
"""

from .generator import MCPCodeGenerator
from .schema_parser import SchemaParser
from .templates import TemplateRenderer

__version__ = "0.1.0"
__author__ = "Michael Oluwaseyi"
__email__ = "michael@crop2cash.com"

__all__ = [
    "MCPCodeGenerator",
    "SchemaParser",
    "TemplateRenderer",
]
