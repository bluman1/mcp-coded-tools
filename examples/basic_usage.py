"""
Basic example: Generate code from an MCP server

This example shows how to:
1. Connect to an MCP server
2. Generate discoverable code
3. Use the generated tools in your agent
"""

import asyncio
from mcp_agent_tools import MCPCodeGenerator


async def main():
    # Initialize the generator
    generator = MCPCodeGenerator()

    # Connect to an MCP server
    # This example uses the Google Drive MCP server
    # Install it first: npm install -g @modelcontextprotocol/server-gdrive
    print("📡 Connecting to Google Drive MCP server...")
    await generator.connect_and_scan(["npx", "-y", "@modelcontextprotocol/server-gdrive"])

    # List discovered tools
    print(f"\n✅ Discovered {len(generator.tools)} tools:")
    for tool_name in generator.list_tools():
        info = generator.get_tool_info(tool_name)
        print(f"  • {info['function_name']}: {info['description'][:60]}...")

    # Generate code
    print("\n✍️  Generating code...")
    generated_files = generator.generate_code(
        output_dir="./generated_servers", server_name="google_drive"
    )

    print(f"\n🎉 Success! Generated {sum(len(f) for f in generated_files.values())} files")
    print("\n📁 Files created:")
    for server, files in generated_files.items():
        print(f"\n  {server}:")
        for file_path in files[:3]:  # Show first 3 files
            print(f"    - {file_path}")

    print("\n💡 Next steps:")
    print("  1. Look at the generated code in ./generated_servers/")
    print("  2. Import in your agent: from generated_servers.google_drive import get_document")
    print("  3. Initialize MCP session and use the tools!")


if __name__ == "__main__":
    asyncio.run(main())
