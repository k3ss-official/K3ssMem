import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.neo4j_client import Neo4jClient
from app.mcp_handler import handle_mcp_request

app = FastAPI(
    title="The Borg Collective Memory System",
    description="A Composite MCP Server for unified knowledge.",
    version="0.1.0",
)

neo4j_client: Neo4jClient | None = None

@app.on_event("startup")
async def startup_event():
    """On startup, connect to the Neo4j database."""
    global neo4j_client
    neo4j_client = Neo4jClient(uri=settings.NEO4J_URI, user=settings.NEO4J_USER, password=settings.NEO4J_PASSWORD)
    try:
        await neo4j_client.verify_connection()
        print("Successfully connected to Neo4j.")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        # In a real app, you might want to prevent startup if the DB is down.
        neo4j_client = None

@app.on_event("shutdown")
async def shutdown_event():
    """On shutdown, close the connection to the Neo4j database."""
    if neo4j_client:
        await neo4j_client.close()
        print("Neo4j connection closed.")

@app.get("/")
def read_root():
    return {"message": "The Borg is online. Resistance is futile."}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Main MCP endpoint. This will handle all incoming JSON-RPC requests.
    """
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    mcp_body = await request.json()
    
    # Delegate the complex logic to a dedicated handler function
    response_body = await handle_mcp_request(mcp_body, neo4j_client)
    
    return JSONResponse(content=response_body)
