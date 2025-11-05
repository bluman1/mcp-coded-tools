"""
Integration tests for MCPCodeGenerator
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.types import Tool
from mcp_agent_tools.generator import MCPCodeGenerator


class TestMCPCodeGeneratorIntegration:
    """Integration tests for the complete code generation workflow."""

    @pytest.fixture
    def mock_tools(self):
        """Create mock tool definitions."""
        return [
            Tool(
                name="gdrive_getDocument",
                description="Retrieves a document from Google Drive",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "documentId": {"type": "string", "description": "The ID of the document"},
                        "fields": {"type": "string", "description": "Specific fields to return"},
                    },
                    "required": ["documentId"],
                },
            ),
            Tool(
                name="gdrive_listFiles",
                description="Lists files in Google Drive",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "folderId": {
                            "type": "string",
                            "description": "Folder ID to list files from",
                        },
                        "maxResults": {
                            "type": "integer",
                            "description": "Maximum number of results",
                        },
                    },
                    "required": ["folderId"],
                },
            ),
            Tool(
                name="salesforce_updateRecord",
                description="Updates a record in Salesforce",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "objectType": {
                            "type": "string",
                            "description": "Type of Salesforce object",
                        },
                        "recordId": {"type": "string", "description": "ID of the record to update"},
                        "data": {"type": "object", "description": "Fields to update"},
                    },
                    "required": ["objectType", "recordId", "data"],
                },
            ),
        ]

    @pytest.mark.asyncio
    async def test_full_code_generation_workflow(self, mock_tools):
        """Test the complete workflow from scan to code generation."""
        generator = MCPCodeGenerator()

        # Mock the MCP connection
        with patch("mcp_agent_tools.generator.stdio_client") as mock_client:
            # Setup mock session
            mock_session = AsyncMock()
            mock_session.initialize = AsyncMock()

            # Mock tools response
            mock_tools_response = MagicMock()
            mock_tools_response.tools = mock_tools
            mock_session.list_tools = AsyncMock(return_value=mock_tools_response)

            # Setup context manager returns
            mock_client.return_value.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_client.return_value.__aexit__ = AsyncMock()

            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock()

            with patch("mcp_agent_tools.generator.ClientSession", return_value=mock_session_cm):
                # Scan the mock server
                await generator.connect_and_scan(["npx", "-y", "mock-server"])

        # Verify tools were scanned
        assert len(generator.tools) == 3
        assert "gdrive_getDocument" in generator.tools
        assert "salesforce_updateRecord" in generator.tools

        # Generate code in temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_code(output_dir=tmpdir, overwrite=True)

            # Verify directory structure
            output_path = Path(tmpdir)
            assert (output_path / "gdrive").exists()
            assert (output_path / "salesforce").exists()
            assert (output_path / "_client.py").exists()

            # Verify gdrive tools
            gdrive_path = output_path / "gdrive"
            assert (gdrive_path / "__init__.py").exists()
            assert (gdrive_path / "get_document.py").exists()
            assert (gdrive_path / "list_files.py").exists()

            # Verify salesforce tools
            salesforce_path = output_path / "salesforce"
            assert (salesforce_path / "__init__.py").exists()
            assert (salesforce_path / "update_record.py").exists()

            # Verify generated code content
            get_doc_code = (gdrive_path / "get_document.py").read_text()
            assert "async def get_document" in get_doc_code
            assert "document_id: str" in get_doc_code
            assert "Optional[str]" in get_doc_code
            assert "gdrive_getDocument" in get_doc_code

            # Verify init exports
            init_code = (gdrive_path / "__init__.py").read_text()
            assert "from .get_document import get_document" in init_code
            assert "from .list_files import list_files" in init_code

            # Verify client code
            client_code = (output_path / "_client.py").read_text()
            assert "async def call_mcp_tool" in client_code
            assert "set_session" in client_code

    def test_list_servers(self):
        """Test listing discovered servers."""
        generator = MCPCodeGenerator()

        # Add mock tools
        generator.tools = {
            "gdrive_getDocument": MagicMock(name="gdrive_getDocument"),
            "gdrive_listFiles": MagicMock(name="gdrive_listFiles"),
            "salesforce_updateRecord": MagicMock(name="salesforce_updateRecord"),
        }

        servers = generator.list_servers()
        assert "gdrive" in servers
        assert "salesforce" in servers
        assert len(servers) == 2

    def test_list_tools_by_server(self):
        """Test listing tools filtered by server."""
        generator = MCPCodeGenerator()

        generator.tools = {
            "gdrive_getDocument": MagicMock(name="gdrive_getDocument"),
            "gdrive_listFiles": MagicMock(name="gdrive_listFiles"),
            "salesforce_updateRecord": MagicMock(name="salesforce_updateRecord"),
        }

        gdrive_tools = generator.list_tools("gdrive")
        assert "gdrive_getDocument" in gdrive_tools
        assert "gdrive_listFiles" in gdrive_tools
        assert len(gdrive_tools) == 2

        sf_tools = generator.list_tools("salesforce")
        assert "salesforce_updateRecord" in sf_tools
        assert len(sf_tools) == 1

    def test_get_tool_info(self):
        """Test retrieving tool information."""
        generator = MCPCodeGenerator()

        mock_tool = Tool(
            name="gdrive_getDocument", description="Gets a document", inputSchema={"type": "object"}
        )

        generator.tools = {"gdrive_getDocument": mock_tool}

        info = generator.get_tool_info("gdrive_getDocument")
        assert info is not None
        assert info["name"] == "gdrive_getDocument"
        assert info["description"] == "Gets a document"
        assert info["function_name"] == "get_document"

    def test_generate_with_explicit_server_name(self):
        """Test generating code with explicit server name."""
        generator = MCPCodeGenerator()

        generator.tools = {
            "tool1": Tool(
                name="tool1", description="Tool 1", inputSchema={"type": "object", "properties": {}}
            )
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            generated_files = generator.generate_code(
                output_dir=tmpdir, server_name="my_custom_server", overwrite=True
            )

            # Verify custom server name was used
            output_path = Path(tmpdir)
            assert (output_path / "my_custom_server").exists()
            assert "my_custom_server" in generated_files

    def test_overwrite_control(self):
        """Test that overwrite flag is respected."""
        generator = MCPCodeGenerator()

        generator.tools = {
            "test_tool": Tool(
                name="test_tool",
                description="Test",
                inputSchema={"type": "object", "properties": {}},
            )
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # First generation
            generator.generate_code(output_dir=tmpdir, server_name="test")

            # Write custom content
            custom_file = Path(tmpdir) / "test" / "tool.py"
            custom_file.write_text("# CUSTOM CONTENT")

            # Try to regenerate without overwrite
            generator.generate_code(output_dir=tmpdir, server_name="test", overwrite=False)

            # Verify custom content is preserved
            assert "# CUSTOM CONTENT" in custom_file.read_text()

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        generator = MCPCodeGenerator()

        with patch("mcp_agent_tools.generator.stdio_client") as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            with pytest.raises(ConnectionError):
                await generator.connect_and_scan(["invalid", "command"])

    def test_generate_without_scan_raises_error(self):
        """Test that generating without scanning raises an error."""
        generator = MCPCodeGenerator()

        with pytest.raises(ValueError, match="No tools available"):
            generator.generate_code()
