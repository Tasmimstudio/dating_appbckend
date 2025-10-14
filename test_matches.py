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
print("TESTING POTENTIAL MATCHES FOR EACH USER")
print("=" * 60)

with driver.session(database=NEO4J_DATABASE) as session:
    # Get all users
    all_users = session.run('MATCH (u:User) RETURN u.user_id as user_id, u.name as name, u.email as email ORDER BY u.name')
    users_list = list(all_users)

    for user in users_list:
        print(f'\n{user["name"]} ({user["email"]}):')
        print('-' * 60)

        # Get potential matches for this user
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (other:User)
        WHERE other.user_id <> $user_id
        AND NOT (u)-[:SWIPED]->(other)
        RETURN other.name as match_name, other.email as match_email
        LIMIT 50
        """

        matches = session.run(query, {"user_id": user["user_id"]})
        match_list = list(matches)

        print(f'  Potential matches: {len(match_list)}')
        for match in match_list:
            print(f'    - {match["match_name"]} ({match["match_email"]})')

driver.close()
print("\n" + "=" * 60)
