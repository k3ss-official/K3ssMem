import httpx
from app.config import settings

async def get_embedding(text: str) -> list[float]:
    """
    Gets an embedding vector for the given text from a local model API.
    """
    # In a real app, the model name could also be a setting
    payload = {
        "model": "nomic-embed-text", # Our chosen local embedding model
        "prompt": text
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.LOCAL_EMBEDDING_URL, json=payload, timeout=30.0)
            response.raise_for_status()
            # The response structure may vary depending on the local server.
            # Ollama returns a dictionary with an "embedding" key.
            data = response.json()
            if "embedding" in data:
                return data["embedding"]
            elif "embeddings" in data:
                return data["embeddings"]
            else:
                print(f"Warning: 'embedding' or 'embeddings' key not found in response from {settings.LOCAL_EMBEDDING_URL}")
                return [0.0] * 384 # Fallback

    except httpx.RequestError as e:
        print(f"Error requesting embedding: {e}")
        # Return a zero vector or handle the error as appropriate
        return [0.0] * 384 # Default dimension for some models
    except Exception as e:
        print(f"An unexpected error occurred in get_embedding: {e}")
        return [0.0] * 384
