from app.config import driver, NEO4J_URI, NEO4J_USER, NEO4J_DATABASE

print(f"Testing connection to Neo4j...")
print(f"URI: {NEO4J_URI}")
print(f"User: {NEO4J_USER}")
print(f"Database: {NEO4J_DATABASE}")
print("-" * 50)

try:
    # Verify connectivity
    driver.verify_connectivity()
    print("[OK] Connection successful!")

    # Test a simple query
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        print(f"[OK] Query test successful! Result: {record['test']}")

    print("\n[OK] Database connection is working properly!")

except Exception as e:
    print(f"[FAILED] Connection failed!")
    print(f"Error: {type(e).__name__}: {str(e)}")
finally:
    driver.close()
