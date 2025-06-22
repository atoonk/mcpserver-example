from fastmcp import FastMCP
from fastmcp.server.http import create_streamable_http_app, create_sse_app
from starlette.routing import Mount
import uvicorn
import fastmcp.settings
import random


# Initialize the MCP server
mcp = FastMCP("Andree's MCP Server", version="0.1.0")

# Define a tool
@mcp.tool
def calculate(expression: str) -> float:
    """Evaluates a simple math expression."""
    return eval(expression, {"__builtins__": {}})

@mcp.tool
def capitalize(text: str) -> str:
    """Capitalize the first letter of every word in the input text."""
    return text.title()


@mcp.tool
def random_word(words: str) -> str:
    """Pick a random word from a comma-separated list."""
    word_list = [w.strip() for w in words.split(",")]
    return random.choice(word_list)


if __name__ == "__main__":
    # Load config
    debug = fastmcp.settings.debug
    auth = mcp.auth

    # Create SSE app under /sse/
    sse_app = create_sse_app(
        server=mcp,
        sse_path="/",
        message_path="/message/",
        auth=auth,
        debug=debug,
    )

    # Create the main app, mounting both transports
    app = create_streamable_http_app(
        server=mcp,
        streamable_http_path="/shttp/",
        auth=auth,
        debug=debug,
        routes=[
            Mount("/sse/", sse_app),
        ],
    )

    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8008)
