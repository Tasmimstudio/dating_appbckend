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
print("CHECKING SWIPE RELATIONSHIPS")
print("=" * 60)

with driver.session(database=NEO4J_DATABASE) as session:
    # Get all swipes
    result = session.run('''
        MATCH (from:User)-[s:SWIPED]->(to:User)
        RETURN from.name as from_name, from.user_id as from_id,
               to.name as to_name, to.user_id as to_id,
               s.action as action
        ORDER BY from_name
    ''')
    swipes = list(result)

    print(f'\nTotal swipes in database: {len(swipes)}')

    if swipes:
        print('\nSwipe Details:')
        print("-" * 60)
        for idx, swipe in enumerate(swipes, 1):
            print(f'{idx}. {swipe["from_name"]} -> {swipe["to_name"]} ({swipe["action"]})')
    else:
        print('\nNo swipes found in database.')

    # Get users who have been swiped on
    print("\n" + "=" * 60)
    print("USERS WHO HAVE SWIPED (and count)")
    print("=" * 60)

    result = session.run('''
        MATCH (from:User)-[s:SWIPED]->(to:User)
        RETURN from.name as name, from.user_id as user_id, count(s) as swipe_count
        ORDER BY swipe_count DESC
    ''')

    for record in result:
        print(f'{record["name"]}: {record["swipe_count"]} swipes')

driver.close()
print("\n" + "=" * 60)
