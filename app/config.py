# app/config.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from pathlib import Path
import time

# Load .env from project root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

print("=" * 60)
print("NEO4J AURA DATABASE CONNECTION")
print("=" * 60)
print(f"URI: {NEO4J_URI}")
print(f"User: {NEO4J_USER}")
print(f"Database: {NEO4J_DATABASE}")
print("-" * 60)

# Initialize driver (doesn't establish connection yet)
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
    connection_timeout=15,  # 15 second timeout
    max_connection_lifetime=3600  # 1 hour max connection lifetime
)

# Test connection with retry logic (but don't crash if it fails)
connection_successful = False
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (u:User) RETURN count(u) as user_count")
            record = result.single()
            user_count = record["user_count"]

        connection_successful = True
        print("STATUS: CONNECTED TO NEO4J AURA")
        print(f"Total users in database: {user_count}")
        print("=" * 60)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Connection attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
        else:
            print("STATUS: FAILED TO CONNECT TO NEO4J")
            print(f"ERROR: {str(e)}")
            print("WARNING: Application will start but database operations will fail")
            print("=" * 60)

def get_db():
    """
    Get a database session.
    Note: This may fail if the database connection is down.
    Always wrap database operations in try-except blocks.
    """
    return driver.session(database=NEO4J_DATABASE)
