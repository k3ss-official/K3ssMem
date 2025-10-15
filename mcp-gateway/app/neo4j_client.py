from neo4j import AsyncGraphDatabase, AsyncDriver

class Neo4jClient:
    """A client for interacting with a Neo4j database."""

    def __init__(self, uri, user, password):
        self.driver: AsyncDriver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Closes the connection to the database."""
        await self.driver.close()

    async def verify_connection(self):
        """Verifies the connection to the database by running a simple query."""
        try:
            await self.driver.verify_connectivity()
        except Exception as e:
            print(f"Failed to verify connectivity: {e}")
            raise

    async def execute_query(self, query: str, params: dict = None):
        """Executes a given Cypher query."""
        params = params or {}
        async with self.driver.session() as session:
            result = await session.run(query, params)
            return await result.data()

    async def semantic_search(self, query: str, limit: int = 5) -> list[dict]:
        """Performs a semantic search for entities in the Neo4j database."""
        from app.embedding_client import get_embedding

        # 1. Get embedding for the query
        query_embedding = await get_embedding(query)
        if not query_embedding:
            return []

        # 2. Perform vector similarity search in Neo4j
        # This Cypher query is adapted from memento-mcp's Neo4jVectorStore.ts
        search_query = """
        CALL db.index.vector.queryNodes(
            'entity_embeddings',
            $limit,
            $embedding
        )
        YIELD node, score
        RETURN node.name AS name, node.entityType AS entityType, score, node.observations AS observations
        ORDER BY score DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(search_query, {"limit": limit, "embedding": query_embedding})
            return await result.data()

    async def create_entities(self, entities: list[dict]):
        """Creates new entities in the Neo4j database."""
        # This query is a direct translation of the one in memento-mcp
        create_query = """
        UNWIND $entities as entity_data
        CREATE (e:Entity {
            id: entity_data.id,
            name: entity_data.name,
            entityType: entity_data.entityType,
            observations: entity_data.observations,
            embedding: entity_data.embedding,
            version: 1,
            createdAt: timestamp(),
            updatedAt: timestamp(),
            validFrom: timestamp(),
            validTo: null,
            changedBy: null
        })
        RETURN e
        """
        
        from app.embedding_client import get_embedding
        import uuid

        entities_to_create = []
        for entity in entities:
            # Create the text to be embedded from observations
            text_to_embed = '\n'.join(entity.get("observations", []))
            
            # Get the embedding vector (placeholder for local model call)
            embedding_vector = await get_embedding(text_to_embed)

            entities_to_create.append({
                "id": str(uuid.uuid4()),
                "name": entity["name"],
                "entityType": entity["entityType"],
                "observations": entity.get("observations", []),
                "embedding": embedding_vector,
            })

        if not entities_to_create:
            return []

        async with self.driver.session() as session:
            result = await session.run(create_query, {"entities": entities_to_create})
            return await result.data()

    async def create_relations(self, relations: list[dict]) -> list[dict]:
        """Creates new relations between entities in the Neo4j database."""
        if not relations:
            return []

        import uuid
        
        created_relations = []
        
        async with self.driver.session() as session:
            async with session.begin_transaction() as tx:
                for relation in relations:
                    # Generate unique ID and timestamp
                    relation_id = str(uuid.uuid4())
                    now = int(self.driver.get_server_info().protocol_version)  # Placeholder for timestamp
                    
                    # Check if both entities exist
                    check_query = """
                    MATCH (from:Entity {name: $fromName})
                    MATCH (to:Entity {name: $toName})
                    RETURN from, to
                    """
                    
                    check_result = await tx.run(check_query, {
                        "fromName": relation["from"],
                        "toName": relation["to"]
                    })
                    
                    records = await check_result.data()
                    
                    # Skip if either entity doesn't exist
                    if not records:
                        print(f"Warning: Skipping relation - entities not found ({relation['from']} -> {relation['to']})")
                        continue
                    
                    # Create the relation
                    create_query = """
                    MATCH (from:Entity {name: $fromName})
                    MATCH (to:Entity {name: $toName})
                    CREATE (from)-[r:RELATES_TO {
                        id: $id,
                        relationType: $relationType,
                        strength: $strength,
                        confidence: $confidence,
                        metadata: $metadata,
                        version: 1,
                        createdAt: timestamp(),
                        updatedAt: timestamp(),
                        validFrom: timestamp(),
                        validTo: null,
                        changedBy: $changedBy
                    }]->(to)
                    RETURN r, from.name AS fromName, to.name AS toName
                    """
                    
                    params = {
                        "id": relation_id,
                        "fromName": relation["from"],
                        "toName": relation["to"],
                        "relationType": relation["relationType"],
                        "strength": relation.get("strength"),
                        "confidence": relation.get("confidence"),
                        "metadata": str(relation.get("metadata")) if relation.get("metadata") else None,
                        "changedBy": relation.get("changedBy")
                    }
                    
                    result = await tx.run(create_query, params)
                    result_data = await result.data()
                    
                    if result_data:
                        record = result_data[0]
                        rel_props = dict(record["r"])
                        
                        created_relation = {
                            "from": record["fromName"],
                            "to": record["toName"],
                            "relationType": rel_props["relationType"],
                            "strength": rel_props.get("strength"),
                            "confidence": rel_props.get("confidence"),
                            "metadata": rel_props.get("metadata")
                        }
                        created_relations.append(created_relation)
        
        return created_relations
