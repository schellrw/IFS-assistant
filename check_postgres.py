#!/usr/bin/env python
"""
Script to check PostgreSQL connectivity on different ports.
"""
import socket
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'R0undlake2_')
db_name = os.environ.get('DB_NAME', 'ifs_assistant')

# Test socket connection on both ports
ports = [5432, 5433]
db_host = "localhost"

print("\nTesting PostgreSQL ports for connectivity:")
for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((db_host, port))
    status = "OPEN" if result == 0 else "CLOSED"
    print(f"Port {port}: {status}")
    sock.close()

# Try to connect to PostgreSQL on both ports and check for pgvector
for port in ports:
    if port == 5433:
        print("\nTrying PostgreSQL on port 5433 (Docker with pgvector):")
    else:
        print("\nTrying PostgreSQL on port 5432 (Standard port):")
    
    try:
        # Connect to PostgreSQL
        conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{port}/{db_name}"
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        print(f"✅ Connected to PostgreSQL on port {port}")
        
        # Check if pgvector extension is available
        try:
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            if cur.fetchone():
                print("✅ pgvector extension is installed")
            else:
                print("❌ pgvector extension is NOT installed")
        except Exception as e:
            print(f"Error checking pgvector: {e}")
        
        # Close connection
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

print("\nRecommended action:")
print("Edit your .env file to use the port where PostgreSQL is running and pgvector is installed") 