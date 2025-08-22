"""
WSGI entry point for production deployment
Used by Gunicorn and other WSGI servers
"""

import os
from app import app, db
from dummy_data import create_dummy_staff, create_dummy_patients, create_dummy_case_notes
import boto3

# Create database tables and dummy data if needed
with app.app_context():
    db.create_all()
    
    # Check if we need to create dummy data
    from app import Staff
    if Staff.query.count() == 0:
        try:
            # Initialize S3 client for dummy data creation
            s3_client = boto3.client(
                's3',
                aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'),
                region_name=app.config.get('AWS_REGION', 'us-east-1')
            )
            
            create_dummy_staff(db)
            create_dummy_patients(db)
            create_dummy_case_notes(db, s3_client, app.config.get('AWS_S3_BUCKET'))
            
        except Exception as e:
            print(f"Warning: Could not create dummy data: {e}")

# This is what WSGI servers will use
application = app

if __name__ == "__main__":
    application.run()

