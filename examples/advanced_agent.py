"""
Advanced example: Using generated MCP tools in an agent

This example shows how to:
1. Generate code from multiple MCP servers
2. Initialize MCP sessions in an agent
3. Use the generated tools for complex workflows
4. Handle errors and manage context efficiently
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# First, generate the code (run this once)
async def generate_tools():
    """Generate code from MCP servers."""
    from mcp_agent_tools import MCPCodeGenerator

    generator = MCPCodeGenerator()

    print("📡 Generating tools from MCP servers...")

    # Connect to Google Drive server
    await generator.connect_and_scan(["npx", "-y", "@modelcontextprotocol/server-gdrive"])

    # You could connect to more servers here
    # await generator.connect_and_scan(["python", "salesforce_server.py"])

    # Generate code
    generator.generate_code(output_dir="./servers", overwrite=True)

    print("✅ Tools generated in ./servers/")


# Agent that uses the generated tools
async def run_agent():
    """
    Example agent that uses generated MCP tools.

    This agent:
    - Connects to an MCP server
    - Initializes the generated tool client
    - Executes a workflow using multiple tools
    """
    print("🤖 Starting agent with MCP tools...")

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="npx", args=["-y", "@modelcontextprotocol/server-gdrive"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Initialize the generated MCP client
            # This makes the tools available for use
            from servers._client import set_session

            set_session(session)

            print("✅ MCP session initialized")

            # Now we can use the generated tools!
            # Import them like normal Python functions
            from servers.gdrive import get_document, list_files

            try:
                # Example workflow: List files and get a document
                print("\n📂 Listing files...")

                # The agent can now call tools with proper typing
                # and without passing everything through the context window
                files = await list_files(folder_id="root", max_results=10)

                print(f"Found {len(files)} files")

                # Process files in code (doesn't go through LLM context)
                pdf_files = [f for f in files if f.get("mimeType") == "application/pdf"]
                print(f"Filtered to {len(pdf_files)} PDFs")

                # Get a specific document
                if pdf_files:
                    doc_id = pdf_files[0]["id"]
                    print(f"\n📄 Fetching document {doc_id}...")

                    document = await get_document(document_id=doc_id, fields="name,mimeType,size")

                    print(f"Got document: {document.get('name')}")
                    print(f"Size: {document.get('size')} bytes")

                print("\n✅ Agent workflow completed successfully!")

            except Exception as e:
                print(f"❌ Error in agent workflow: {e}")
                raise


async def agent_with_complex_workflow():
    """
    More complex agent workflow demonstrating context efficiency.

    This shows how code execution with MCP keeps intermediate
    results out of the LLM context window.
    """
    print("🤖 Running complex agent workflow...")

    # Setup MCP connection (same as above)
    server_params = StdioServerParameters(
        command="npx", args=["-y", "@modelcontextprotocol/server-gdrive"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            from servers._client import set_session

            set_session(session)

            from servers.gdrive import list_files

            print("\n📊 Analyzing all documents...")

            # Get all files
            all_files = await list_files(folder_id="root", max_results=100)

            # Process in code - agent only sees summary, not all data
            doc_files = [f for f in all_files if "document" in f.get("mimeType", "")]

            # Calculate statistics without flooding context
            total_size = sum(int(f.get("size", 0)) for f in doc_files)
            avg_size = total_size / len(doc_files) if doc_files else 0

            print(f"  • Found {len(doc_files)} documents")
            print(f"  • Total size: {total_size / 1024 / 1024:.2f} MB")
            print(f"  • Average size: {avg_size / 1024:.2f} KB")

            # Only log summary to agent's output (what goes in context)
            print("\n📝 Summary for agent:")
            print(f"Analyzed {len(doc_files)} documents, average size {avg_size/1024:.1f}KB")

            # Agent can continue with filtered data, context window stays small


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Generate tools first
        await generate_tools()
    else:
        # Run the agent
        try:
            # Simple workflow
            await run_agent()

            print("\n" + "=" * 60)

            # Complex workflow
            await agent_with_complex_workflow()

        except ImportError:
            print("\n❌ Generated tools not found!")
            print("Run this first: python advanced_agent.py generate")
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Advanced MCP CodeGen Agent Example")
    print("=" * 60)
    asyncio.run(main())
