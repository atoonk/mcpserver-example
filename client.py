#!/usr/bin/env python3
"""
Simple MCP SSE client.
Connects to the MCP server via SSE, initializes the session, lists all tools,
and invokes the 'calculate' tool.
"""
import requests
import json

def parse_sse(url):
    """
    Generator that yields (event, data) tuples from an SSE stream.
    """
    with requests.get(url, stream=True) as response:
        event = None
        data_lines = []
        for raw in response.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            line = raw.strip()
            # Empty line indicates dispatch
            if not line:
                if event and data_lines:
                    yield event, "\n".join(data_lines)
                event = None
                data_lines = []
                continue
            if line.startswith("event:"):
                event = line[len("event:"):].strip()
            elif line.startswith("data:"):
                data_lines.append(line[len("data:"):].strip())

def main():
    base_url = "http://127.0.0.1:8008"
    sse_url = base_url + "/sse/"
    print(f"Connecting to SSE endpoint: {sse_url}")
    message_url = None
    next_id = 1
    state = 0

    for event, data in parse_sse(sse_url):
        if event == "endpoint":
            # data contains the message endpoint path with session_id query
            message_url = base_url.rstrip("/") + data
            print(f"Message endpoint: {message_url}")
            # Send initialize request
            init_req = {
                "jsonrpc": "2.0",
                "id": next_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": 1,
                    "capabilities": {},
                    "clientInfo": {"name": "client.py", "version": "0.1.0"}
                }
            }
            requests.post(message_url, json=init_req)
            next_id += 1
            state = 1
        elif event == "message":
            msg = json.loads(data)
            # Initialization result
            if state == 1 and msg.get("id") == 1:
                print("Initialized:", msg.get("result"))
                # Send initialized notification
                init_notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": None}
                requests.post(message_url, json=init_notif)
                # List tools
                list_req = {"jsonrpc": "2.0", "id": next_id, "method": "tools/list", "params": {}}
                requests.post(message_url, json=list_req)
                next_id += 1
                state = 2
            # Tools list result
            elif state == 2 and msg.get("id") == 2:
                tools = msg["result"].get("tools", [])
                print("Available tools:")
                for tool in tools:
                    print(f" - {tool.get('name')}: {tool.get('description')}")
                # Invoke calculate tool
                call_req = {
                    "jsonrpc": "2.0",
                    "id": next_id,
                    "method": "tools/call",
                    "params": {"name": "calculate", "arguments": {"expression": "7*6"}}
                }
                requests.post(message_url, json=call_req)
                next_id += 1
                state = 3
            # Calculation result
            elif state == 3 and msg.get("id") == 3:
                result = msg["result"].get("content", [])
                print("Calculation result content:", result)
                break

if __name__ == "__main__":
    main()