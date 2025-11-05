"""
Parse JSON schemas from MCP tools into Python type annotations
"""

from typing import Any, Dict, List, Set
import inflection


class SchemaParser:
    """
    Parse JSON Schema to extract Python function signatures and types.
    """

    def __init__(self) -> None:
        self.type_map = {
            "string": "str",
            "number": "float",
            "integer": "int",
            "boolean": "bool",
            "object": "Dict[str, Any]",
            "array": "List[Any]",
            "null": "None",
        }

    def parse(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a JSON schema into Python function components.

        Args:
            schema: JSON schema object from MCP tool definition

        Returns:
            Dictionary with 'parameters', 'signature', and 'dict_items'
        """
        if not schema:
            return {"parameters": [], "signature": "", "dict_items": ""}

        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        parameters = []
        signature_parts = []
        dict_items = []

        for prop_name, prop_def in properties.items():
            param_info = self._parse_property(prop_name, prop_def, prop_name in required)
            parameters.append(param_info)
            signature_parts.append(param_info["signature"])
            dict_items.append(param_info["dict_item"])

        return {
            "parameters": parameters,
            "signature": ", ".join(signature_parts) if signature_parts else "",
            "dict_items": ", ".join(dict_items) if dict_items else "",
        }

    def _parse_property(
        self, prop_name: str, prop_def: Dict[str, Any], is_required: bool
    ) -> Dict[str, Any]:
        """Parse a single property from the schema."""
        py_name = inflection.underscore(prop_name)
        py_type = self._json_type_to_python(prop_def)
        description = prop_def.get("description", "")

        # Build signature component
        if is_required:
            signature = f"{py_name}: {py_type}"
        else:
            signature = f"{py_name}: Optional[{py_type}] = None"

        # Build dictionary item for tool call
        dict_item = f"'{prop_name}': {py_name}"

        return {
            "name": py_name,
            "original_name": prop_name,
            "type": py_type,
            "required": is_required,
            "description": description,
            "signature": signature,
            "dict_item": dict_item,
        }

    def _json_type_to_python(self, prop_def: Dict[str, Any]) -> str:
        """
        Convert JSON schema type to Python type annotation.

        Handles:
        - Basic types (string, number, integer, boolean)
        - Arrays with item types
        - Objects
        - Enums
        - anyOf/oneOf unions
        """
        # Handle anyOf/oneOf (union types)
        if "anyOf" in prop_def:
            types = [self._json_type_to_python(t) for t in prop_def["anyOf"]]
            return f"Union[{', '.join(types)}]"

        if "oneOf" in prop_def:
            types = [self._json_type_to_python(t) for t in prop_def["oneOf"]]
            return f"Union[{', '.join(types)}]"

        # Handle enum (literal types)
        if "enum" in prop_def:
            values = prop_def["enum"]
            if all(isinstance(v, str) for v in values):
                literals = ", ".join(f'"{v}"' for v in values)
                return f"Literal[{literals}]"
            else:
                # Mixed types in enum - just use Any
                return "Any"

        # Get the type
        json_type = prop_def.get("type")

        if not json_type:
            return "Any"

        # Handle arrays
        if json_type == "array":
            items = prop_def.get("items", {})
            if items:
                item_type = self._json_type_to_python(items)
                return f"List[{item_type}]"
            return "List[Any]"

        # Handle objects
        if json_type == "object":
            # Check if there are specific properties defined
            if "properties" in prop_def:
                # Could generate TypedDict here, but Dict is simpler
                return "Dict[str, Any]"

            # Check for additionalProperties type
            additional = prop_def.get("additionalProperties")
            if additional and isinstance(additional, dict):
                value_type = self._json_type_to_python(additional)
                return f"Dict[str, {value_type}]"

            return "Dict[str, Any]"

        # Basic types
        return self.type_map.get(json_type, "Any")

    def extract_imports(self, parameters: List[Dict[str, Any]]) -> Set[str]:
        """
        Determine which typing imports are needed based on parameters.

        Args:
            parameters: List of parameter dictionaries from parse()

        Returns:
            Set of import names needed (e.g., {'Optional', 'Dict', 'List'})
        """
        imports = {"Any"}  # Always include Any

        for param in parameters:
            py_type = param["type"]

            # Check for Optional
            if not param["required"]:
                imports.add("Optional")

            # Extract other typing constructs
            if "Dict[" in py_type:
                imports.add("Dict")
            if "List[" in py_type:
                imports.add("List")
            if "Union[" in py_type:
                imports.add("Union")
            if "Literal[" in py_type:
                imports.add("Literal")

        return imports
