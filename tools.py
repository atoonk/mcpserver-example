from fastmcp import FastMCP

mcp = FastMCP(name="SimpleCalc")

@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a basic math expression (e.g. '2 + 3 * 4')"""
    allowed_names = {"__builtins__": {}}
    return float(eval(expression, allowed_names, {}))

