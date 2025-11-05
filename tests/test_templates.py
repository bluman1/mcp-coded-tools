"""
Tests for template renderer
"""

from mcp_agent_tools.templates import TemplateRenderer


class TestTemplateRenderer:
    """Test TemplateRenderer functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.renderer = TemplateRenderer()

    def test_render_simple_tool(self):
        """Test rendering a simple tool function."""
        code = self.renderer.render_tool(
            func_name="get_document",
            tool_name="gdrive_getDocument",
            description="Gets a document",
            parameters=[
                {
                    "name": "document_id",
                    "original_name": "documentId",
                    "type": "str",
                    "required": True,
                    "description": "The document ID",
                }
            ],
            signature="document_id: str",
            dict_items="'documentId': document_id",
        )

        assert "async def get_document(document_id: str)" in code
        assert "from typing import" in code
        assert "call_mcp_tool" in code
        assert "gdrive_getDocument" in code
        assert "Gets a document" in code

    def test_render_tool_with_optional_params(self):
        """Test rendering a tool with optional parameters."""
        code = self.renderer.render_tool(
            func_name="list_files",
            tool_name="gdrive_listFiles",
            description="Lists files",
            parameters=[
                {
                    "name": "folder_id",
                    "original_name": "folderId",
                    "type": "str",
                    "required": True,
                    "description": "Folder ID",
                },
                {
                    "name": "max_results",
                    "original_name": "maxResults",
                    "type": "int",
                    "required": False,
                    "description": "Maximum results",
                },
            ],
            signature="folder_id: str, max_results: Optional[int] = None",
            dict_items="'folderId': folder_id, 'maxResults': max_results",
        )

        assert "Optional[int]" in code
        assert "= None" in code
        assert "Folder ID" in code
        assert "Maximum results" in code

    def test_render_init(self):
        """Test rendering __init__.py."""
        code = self.renderer.render_init(["get_document", "list_files", "create_folder"])

        assert "from .get_document import get_document" in code
        assert "from .list_files import list_files" in code
        assert "from .create_folder import create_folder" in code
        assert "__all__" in code
        assert '"get_document"' in code

    def test_render_client(self):
        """Test rendering MCP client."""
        code = self.renderer.render_client()

        assert "ClientSession" in code
        assert "set_session" in code
        assert "call_mcp_tool" in code
        assert "async def call_mcp_tool" in code
        assert "RuntimeError" in code

    def test_render_readme(self):
        """Test rendering README."""
        servers = [
            {
                "name": "google_drive",
                "count": 3,
                "tools": [
                    {"name": "get_document", "description": "Get a document"},
                    {"name": "list_files", "description": "List files"},
                    {"name": "create_folder", "description": "Create folder"},
                ],
            },
            {
                "name": "salesforce",
                "count": 2,
                "tools": [
                    {"name": "update_record", "description": "Update record"},
                    {"name": "query", "description": "Query records"},
                ],
            },
        ]

        code = self.renderer.render_readme(servers)

        assert "google_drive" in code
        assert "salesforce" in code
        assert "(3 tools)" in code
        assert "(2 tools)" in code
        assert "get_document" in code
        assert "Update record" in code
        assert "Usage" in code

    def test_render_tool_no_parameters(self):
        """Test rendering a tool with no parameters."""
        code = self.renderer.render_tool(
            func_name="get_current_user",
            tool_name="auth_getCurrentUser",
            description="Gets current user",
            parameters=[],
            signature="",
            dict_items="",
        )

        assert "async def get_current_user()" in code
        assert "Dict[str, Any]" in code
        assert "auth_getCurrentUser" in code

    def test_render_tool_with_complex_types(self):
        """Test rendering a tool with complex type annotations."""
        code = self.renderer.render_tool(
            func_name="batch_update",
            tool_name="sheets_batchUpdate",
            description="Batch update",
            parameters=[
                {
                    "name": "requests",
                    "original_name": "requests",
                    "type": "List[Dict[str, Any]]",
                    "required": True,
                    "description": "Update requests",
                }
            ],
            signature="requests: List[Dict[str, Any]]",
            dict_items="'requests': requests",
        )

        assert "List[Dict[str, Any]]" in code
        assert "from typing import" in code
        assert "List" in code
        assert "Dict" in code
