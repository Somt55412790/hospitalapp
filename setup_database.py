#!/usr/bin/env python3
"""
Database setup script for Mental Health Hospital Management System
This script connects to your RDS instance and sets up the required database and tables
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = "database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = "Bayernmunich007$$"
DB_NAME = "hospital_db"
DB_PORT = 5432

def create_database():
    """Create the hospital_db database if it doesn't exist"""
    print("🏥 Setting up Mental Health Hospital Database...")
    
    try:
        # Connect to the default 'postgres' database first
        print(f"Connecting to RDS instance at {DB_HOST}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres',  # Connect to default database first
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if hospital_db exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created successfully!")
        else:
            print(f"✅ Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_connection():
    """Test connection to the hospital_db database"""
    print(f"Testing connection to {DB_NAME} database...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"📊 Database version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error connecting to {DB_NAME}: {e}")
        return False

def setup_flask_tables():
    """Set up Flask application tables"""
    print("Setting up application tables...")
    
    try:
        # Import Flask app and create tables
        from app import app, db
        
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we need to create dummy data
            from app import Staff
            if Staff.query.count() == 0:
                print("No staff found. Creating dummy data...")
                
                try:
                    from dummy_data import create_dummy_staff, create_dummy_patients, create_dummy_case_notes
                    import boto3
                    
                    # Create dummy staff and patients
                    create_dummy_staff(db)
                    create_dummy_patients(db)
                    
                    # Try to create dummy case notes with S3 (will work only if AWS credentials are set)
                    try:
                        s3_client = boto3.client(
                            's3',
                            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                            region_name=os.environ.get('AWS_REGION', 'ap-southeast-2')
                        )
                        create_dummy_case_notes(db, s3_client, os.environ.get('AWS_S3_BUCKET', 'hosptialbuckets3'))
                        print("✅ Dummy data with S3 integration created successfully!")
                    except Exception as e:
                        print(f"⚠️  Could not create S3-integrated dummy data: {e}")
                        print("Creating dummy data without S3 integration...")
                        from dummy_data import create_dummy_case_notes_database_only
                        create_dummy_case_notes_database_only(db)
                        print("✅ Dummy data created successfully (database only)!")
                        
                except ImportError as e:
                    print(f"⚠️  Could not create dummy data: {e}")
            else:
                print("✅ Staff data already exists in database.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Flask tables: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏥 Mental Health Hospital Management System")
    print("Database Setup Script")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    # Step 3: Setup Flask tables
    if not setup_flask_tables():
        print("❌ Failed to setup application tables. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Database setup completed successfully!")
    print("=" * 60)
    print("\n📋 Configuration Summary:")
    print(f"   Database Host: {DB_HOST}")
    print(f"   Database Name: {DB_NAME}")
    print(f"   Database User: {DB_USER}")
    print(f"   S3 Bucket: {os.environ.get('AWS_S3_BUCKET', 'hosptialbuckets3')}")
    print(f"   AWS Region: {os.environ.get('AWS_REGION', 'ap-southeast-2')}")
    print("\n🚀 Your hospital management system is ready!")
    print("\n👥 Demo Login Credentials:")
    print("   Username: dr_smith")
    print("   Password: password123")
    print("\n⚠️  Next Steps:")
    print("   1. Update AWS credentials in .env file")
    print("   2. Start the application with: python run.py")
    print("   3. Access via your EC2 public IP on port 5000")

if __name__ == "__main__":
    main()

