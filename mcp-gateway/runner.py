import uvicorn
import traceback
import os

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting Borg Collective Memory MCP Server on {host}:{port}...")
    try:
        uvicorn.run("main:app", host=host, port=port, log_level=log_level)
    except Exception as e:
        print("!!! FAILED TO START SERVER !!!")
        print(f"Error: {e}")
        traceback.print_exc()
