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
            tx = await session.begin_transaction()
            try:
                for relation in relations:
                    # Generate unique ID
                    relation_id = str(uuid.uuid4())
                    
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
                        
                        created_relation = {
                            "from": record["fromName"],
                            "to": record["toName"],
                            "relationType": relation["relationType"],
                            "strength": relation.get("strength"),
                            "confidence": relation.get("confidence"),
                            "metadata": relation.get("metadata")
                        }
                        created_relations.append(created_relation)
                
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                raise e
        
        return created_relations

    async def add_observations(self, observations_data: list[dict]) -> list[dict]:
        """Adds new observations to existing entities in the Neo4j database."""
        from app.embedding_client import get_embedding

        updated_entities = []
        async with self.driver.session() as session:
            tx = await session.begin_transaction()
            try:
                for obs_item in observations_data:
                    entity_name = obs_item["entityName"]
                    new_contents = obs_item["contents"]
                    
                    # Fetch the existing entity and its observations
                    fetch_query = """
                    MATCH (e:Entity {name: $entityName})
                    RETURN e
                    """
                    result = await tx.run(fetch_query, {"entityName": entity_name})
                    record = await result.single()

                    if not record:
                        print(f"Warning: Entity '{entity_name}' not found. Skipping observation.")
                        continue

                    entity = record["e"]
                    existing_observations = entity.get("observations", [])
                    
                    # Combine existing and new observations
                    combined_observations = list(set(existing_observations + new_contents)) # Use set to avoid duplicates
                    
                    # Create text for new embedding
                    text_to_embed = '\n'.join(combined_observations)
                    embedding_vector = await get_embedding(text_to_embed)

                    # Update the entity
                    update_query = """
                    MATCH (e:Entity {name: $entityName})
                    SET e.observations = $combinedObservations,
                        e.embedding = $embeddingVector,
                        e.updatedAt = timestamp()
                    RETURN e.name AS name, e.observations AS observations
                    """
                    update_result = await tx.run(update_query, {
                        "entityName": entity_name,
                        "combinedObservations": combined_observations,
                        "embeddingVector": embedding_vector
                    })
                    updated_record = await update_result.single()
                    if updated_record:
                        updated_entities.append({
                            "name": updated_record["name"],
                            "observations": updated_record["observations"]
                        })
                
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                raise e
        
        return updated_entities

    async def read_graph(self) -> dict:
        """Reads the entire knowledge graph from Neo4j."""
        import time
        start_time = time.time()
        
        # Load all entities
        entity_query = """
        MATCH (e:Entity)
        RETURN e.name AS name, e.entityType AS entityType, e.observations AS observations
        """
        
        async with self.driver.session() as session:
            entity_result = await session.run(entity_query)
            entity_records = await entity_result.data()
            
            entities = []
            for record in entity_records:
                entities.append({
                    "name": record["name"],
                    "entityType": record["entityType"],
                    "observations": record.get("observations", [])
                })
            
            # Load all relations
            relation_query = """
            MATCH (from:Entity)-[r:RELATES_TO]->(to:Entity)
            RETURN from.name AS fromName, to.name AS toName, r.relationType AS relationType, r.strength AS strength, r.confidence AS confidence
            """
            
            relation_result = await session.run(relation_query)
            relation_records = await relation_result.data()
            
            relations = []
            for record in relation_records:
                relations.append({
                    "from": record["fromName"],
                    "to": record["toName"],
                    "relationType": record.get("relationType"),
                    "strength": record.get("strength"),
                    "confidence": record.get("confidence")
                })
        
        time_taken = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "entities": entities,
            "relations": relations,
            "total": len(entities),
            "timeTaken": time_taken
        }

    async def open_nodes(self, names: list[str]) -> dict:
        """Opens specific nodes by their names and returns them with their relations."""
        import time
        start_time = time.time()
        
        if not names:
            return {"entities": [], "relations": []}
        
        async with self.driver.session() as session:
            # Query for entities by name
            entity_query = """
            MATCH (e:Entity)
            WHERE e.name IN $names
            RETURN e.name AS name, e.entityType AS entityType, e.observations AS observations
            """
            
            entity_result = await session.run(entity_query, {"names": names})
            entity_records = await entity_result.data()
            
            entities = []
            for record in entity_records:
                entities.append({
                    "name": record["name"],
                    "entityType": record["entityType"],
                    "observations": record.get("observations", [])
                })
            
            # Get relations between the specified entities
            relations_query = """
            MATCH (from:Entity)-[r:RELATES_TO]->(to:Entity)
            WHERE from.name IN $names AND to.name IN $names
            RETURN from.name AS fromName, to.name AS toName, r.relationType AS relationType, r.strength AS strength, r.confidence AS confidence
            """
            
            relations_result = await session.run(relations_query, {"names": names})
            relations_records = await relations_result.data()
            
            relations = []
            for record in relations_records:
                relations.append({
                    "from": record["fromName"],
                    "to": record["toName"],
                    "relationType": record.get("relationType"),
                    "strength": record.get("strength"),
                    "confidence": record.get("confidence")
                })
        
        time_taken = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "entities": entities,
            "relations": relations,
            "total": len(entities),
            "timeTaken": time_taken
        }
