#!/usr/bin/env python3
"""
Cleanup script to remove all test data from Neo4j
"""
from neo4j import AsyncGraphDatabase
import asyncio

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "memento_password"

async def cleanup_database():
    """Delete all entities and relations from the database"""
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        async with driver.session() as session:
            # First, get a count of what we're deleting
            count_query = """
            MATCH (e:Entity)
            RETURN count(e) AS entityCount
            """
            result = await session.run(count_query)
            record = await result.single()
            entity_count = record["entityCount"] if record else 0
            
            count_relations_query = """
            MATCH ()-[r:RELATES_TO]->()
            RETURN count(r) AS relationCount
            """
            result = await session.run(count_relations_query)
            record = await result.single()
            relation_count = record["relationCount"] if record else 0
            
            print(f"Found {entity_count} entities and {relation_count} relations")
            
            if entity_count > 0 or relation_count > 0:
                print("Deleting all data...")
                # Delete all nodes and relationships
                delete_query = """
                MATCH (n)
                DETACH DELETE n
                """
                await session.run(delete_query)
                print("✅ Database cleaned successfully!")
                print(f"   Deleted {entity_count} entities and {relation_count} relations")
            else:
                print("✅ Database is already empty.")
    
    finally:
        await driver.close()

if __name__ == "__main__":
    asyncio.run(cleanup_database())
