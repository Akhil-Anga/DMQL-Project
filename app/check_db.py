import pandas as pd
from sqlalchemy import create_engine

# This is the same connection string from your app.py
DB_URL = "postgresql://postgres:Ramaseshu1%40@localhost:5432/postgres"

def check_tables():
    try:
        engine = create_engine(DB_URL)
        
        # Query to list ALL tables in ALL schemas
        query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name;
        """
        
        print("🔍 Connecting to database...")
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("❌ No custom tables found. Did you run 'dbt run'?")
        else:
            print("\n✅ FOUND THESE TABLES:")
            print(df)
            print("\n💡 Look for your 'fact_admission' table in the list above.")
            print("   Then update your app.py query with: schema_name.table_name")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    check_tables()