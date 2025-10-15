import uvicorn
import traceback

if __name__ == "__main__":
    print("Attempting to start server programmatically...")
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print("!!! FAILED TO START SERVER !!!")
        print(f"Error: {e}")
        traceback.print_exc()
