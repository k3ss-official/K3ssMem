#!/opt/homebrew/Caskroom/miniforge/base/envs/K3ssMem/bin/python
"""
STDIO MCP Server Bridge for Borg Collective Memory
Bridges STDIO (for Perplexity/Claude) to HTTP (localhost:8000)
"""
import sys
import json
import requests

HTTP_ENDPOINT = "http://localhost:8000/mcp"

def handle_message(message: dict) -> dict:
    """Forward MCP message to HTTP endpoint and return response."""
    response = requests.post(HTTP_ENDPOINT, json=message, timeout=30)
    return response.json()

def main():
    """Main STDIO loop - read from stdin, write to stdout."""
    # Ensure stderr is used for logging
    print("Borg Collective STDIO MCP Server starting...", file=sys.stderr)
    
    # Read from stdin line by line
    for line in sys.stdin:
        try:
            # Parse incoming JSON-RPC message
            message = json.loads(line.strip())
            
            # Forward to HTTP endpoint
            response = handle_message(message)
            
            # Write response to stdout
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Parse error: {e}"},
                "id": None
            }
            print(json.dumps(error_response), flush=True)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {e}"},
                "id": message.get("id") if 'message' in locals() else None
            }
            print(json.dumps(error_response), flush=True)
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
