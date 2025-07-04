# Database connection management using pymysql
import pymysql
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ConfigManager

def test_connection(config=None):
    """Test database connection with real query"""
    if config is None:
        config = ConfigManager().get_database_config()
    
    try:
        conn = pymysql.connect(
            host=config.get('db_host', 'localhost'),
            port=int(config.get('db_port', 3306)),
            user=config.get('db_user', 'sa'),
            password=config.get('db_password', 'dm257758'),
            charset='utf8mb4',
            connect_timeout=5,
            autocommit=True
        )
        
        # Actually test the connection with a query
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result != (1,):
                raise Exception("Query test failed")
        
        conn.close()
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_connection():
    """Get database connection"""
    config = ConfigManager().get_database_config()
    try:
        conn = pymysql.connect(
            host=config.get('db_host', 'localhost'),
            port=int(config.get('db_port', 3306)),
            user=config.get('db_user', 'sa'),
            password=config.get('db_password', 'dm257758'),
            database=config.get('db_name', 'plan_manager'),
            charset='utf8mb4',
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def execute_sql_statements(cursor, sql_content):
    """Execute SQL statements one by one, handling errors gracefully"""
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current_statement.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current_statement))
            current_statement = []
    
    # Add any remaining statement
    if current_statement:
        statements.append(' '.join(current_statement))
    
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
            print(f"Executed statement {i+1}/{len(statements)}: {stmt[:50]}...")
        except Exception as e:
            # For ALTER TABLE statements that might fail if constraint already exists, just warn
            if "ADD CONSTRAINT" in stmt.upper() and "already exists" in str(e).lower():
                print(f"Warning: Constraint already exists: {stmt[:50]}...")
                continue
            elif "Duplicate entry" in str(e):
                print(f"Warning: Duplicate data ignored: {stmt[:50]}...")
                continue
            else:
                print(f"Error executing statement: {stmt}")
                print(f"Error details: {e}")
                # Don't raise exception, continue with next statement

def init_database():
    """Initialize database tables and data"""
    config = ConfigManager()
    db_config = config.get_database_config()
    
    try:
        # First connect without database to create it
        conn = pymysql.connect(
            host=db_config.get('db_host', 'localhost'),
            port=int(db_config.get('db_port', 3306)),
            user=db_config.get('db_user', 'sa'),
            password=db_config.get('db_password', 'dm257758'),
            charset='utf8mb4',
            autocommit=True
        )
        
        with conn.cursor() as cursor:
            # Create database if not exists
            db_name = db_config.get('db_name', 'plan_manager')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE `{db_name}`")
            
            # Read and execute schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                    
                execute_sql_statements(cursor, schema_sql)
            else:
                raise Exception(f"Schema file not found: {schema_path}")
        
        conn.close()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False