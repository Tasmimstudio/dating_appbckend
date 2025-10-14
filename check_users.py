from app.config import get_db
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 60)
print("CHECKING ALL USERS IN DATABASE")
print("=" * 60)

with driver.session(database=NEO4J_DATABASE) as session:
    # Get all users
    result = session.run('MATCH (u:User) RETURN u ORDER BY u.name')
    users = list(result)

    print(f'\nTotal users in database: {len(users)}')
    print('\nUser Details:')
    print("-" * 60)

    for idx, record in enumerate(users, 1):
        user = record['u']
        print(f'\n{idx}. Name: {user.get("name", "N/A")}')
        print(f'   Email: {user.get("email", "N/A")}')
        print(f'   Age: {user.get("age", "N/A")}')
        print(f'   Gender: {user.get("gender", "N/A")}')
        print(f'   City: {user.get("city", "N/A")}')
        print(f'   Bio: {user.get("bio", "N/A")[:50] if user.get("bio") else "N/A"}...')
        print(f'   User ID: {user.get("user_id", "N/A")}')

driver.close()
print("\n" + "=" * 60)
