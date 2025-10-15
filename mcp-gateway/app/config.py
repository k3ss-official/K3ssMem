from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Model for environment variables. Case-insensitive.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Neo4j connection settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "memento_password"

    # URL for the local embedding model API
    LOCAL_EMBEDDING_URL: str = "http://localhost:11434/api/embeddings" # Default for Ollama

# Create a single, reusable instance of the settings
settings = Settings()
