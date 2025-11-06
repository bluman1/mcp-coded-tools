"""
Tests for schema parser
"""

from mcp_coded_tools.schema_parser import SchemaParser


class TestSchemaParser:
    """Test SchemaParser functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = SchemaParser()

    def test_parse_empty_schema(self):
        """Test parsing empty schema."""
        result = self.parser.parse({})
        assert result["signature"] == ""
        assert result["dict_items"] == ""
        assert result["parameters"] == []

    def test_parse_simple_string_parameter(self):
        """Test parsing a simple string parameter."""
        schema = {
            "type": "object",
            "properties": {"documentId": {"type": "string", "description": "The document ID"}},
            "required": ["documentId"],
        }

        result = self.parser.parse(schema)

        assert len(result["parameters"]) == 1
        param = result["parameters"][0]
        assert param["name"] == "document_id"
        assert param["type"] == "str"
        assert param["required"] is True
        assert param["description"] == "The document ID"
        assert "document_id: str" in result["signature"]
        assert "'documentId': document_id" in result["dict_items"]

    def test_parse_optional_parameter(self):
        """Test parsing an optional parameter."""
        schema = {
            "type": "object",
            "properties": {"fields": {"type": "string", "description": "Optional fields"}},
            "required": [],
        }

        result = self.parser.parse(schema)

        param = result["parameters"][0]
        assert param["required"] is False
        assert "Optional[str]" in result["signature"]
        assert "= None" in result["signature"]

    def test_parse_multiple_parameters(self):
        """Test parsing multiple parameters."""
        schema = {
            "type": "object",
            "properties": {
                "documentId": {"type": "string"},
                "fields": {"type": "string"},
                "includeMetadata": {"type": "boolean"},
            },
            "required": ["documentId"],
        }

        result = self.parser.parse(schema)

        assert len(result["parameters"]) == 3
        assert "document_id: str" in result["signature"]
        assert "fields: Optional[str] = None" in result["signature"]
        assert "include_metadata: Optional[bool] = None" in result["signature"]

    def test_parse_array_type(self):
        """Test parsing array types."""
        schema = {
            "type": "object",
            "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
        }

        result = self.parser.parse(schema)
        param = result["parameters"][0]
        assert param["type"] == "List[str]"

    def test_parse_object_type(self):
        """Test parsing object types."""
        schema = {
            "type": "object",
            "properties": {
                "metadata": {"type": "object", "properties": {"name": {"type": "string"}}}
            },
        }

        result = self.parser.parse(schema)
        param = result["parameters"][0]
        assert param["type"] == "Dict[str, Any]"

    def test_parse_enum_type(self):
        """Test parsing enum types."""
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "approved", "rejected"]}
            },
        }

        result = self.parser.parse(schema)
        param = result["parameters"][0]
        assert "Literal[" in param["type"]
        assert '"pending"' in param["type"]

    def test_parse_union_type(self):
        """Test parsing union types (anyOf)."""
        schema = {
            "type": "object",
            "properties": {"value": {"anyOf": [{"type": "string"}, {"type": "number"}]}},
        }

        result = self.parser.parse(schema)
        param = result["parameters"][0]
        assert "Union[" in param["type"]

    def test_extract_imports_basic(self):
        """Test extracting required imports."""
        parameters = [
            {"name": "doc_id", "type": "str", "required": True},
            {"name": "fields", "type": "str", "required": False},
        ]

        imports = self.parser.extract_imports(parameters)
        assert "Any" in imports
        assert "Optional" in imports

    def test_extract_imports_complex(self):
        """Test extracting imports for complex types."""
        parameters = [
            {"name": "tags", "type": "List[str]", "required": True},
            {"name": "meta", "type": "Dict[str, Any]", "required": True},
            {"name": "status", "type": 'Literal["pending", "done"]', "required": False},
        ]

        imports = self.parser.extract_imports(parameters)
        assert "List" in imports
        assert "Dict" in imports
        assert "Literal" in imports
        assert "Optional" in imports

    def test_snake_case_conversion(self):
        """Test camelCase to snake_case conversion."""
        schema = {
            "type": "object",
            "properties": {
                "documentId": {"type": "string"},
                "includeMetadata": {"type": "boolean"},
                "maxResults": {"type": "integer"},
            },
            "required": ["documentId"],
        }

        result = self.parser.parse(schema)
        param_names = [p["name"] for p in result["parameters"]]

        assert "document_id" in param_names
        assert "include_metadata" in param_names
        assert "max_results" in param_names
