#!/usr/bin/env python3
"""
Simple fastmcp client using the built-in asyncio Client.
"""
import asyncio
from fastmcp.client import Client


async def main():
    # SSE endpoint URL (ensure trailing slash)
    url = "http://127.0.0.1:8008/sse/"
    async with Client(url) as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f" • {tool.name}: {tool.description}")

        # Invoke the 'calculate' tool
        result = await client.call_tool("calculate", {"expression": "7*6"})
        # result is a list of MCPContent objects; extract text if available
        if result:
            first = result[0]
            # TextContent has a 'text' attribute
            text = getattr(first, "text", first)
            print("Calculation result:", text)


if __name__ == "__main__":
    asyncio.run(main())
