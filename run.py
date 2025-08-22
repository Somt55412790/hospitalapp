#!/usr/bin/env python3
"""
Mental Health Hospital Management System
Entry point for running the application
"""

import os
from app import app, db
from dummy_data import create_dummy_staff, create_dummy_patients, create_dummy_case_notes
import boto3
from botocore.exceptions import ClientError

def create_app():
    """Create and configure the Flask application."""
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Check if we need to create dummy data
        from app import Staff
        if Staff.query.count() == 0:
            print("Creating dummy data...")
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
                print("Dummy data created successfully!")
                
            except Exception as e:
                print(f"Warning: Could not create dummy data: {e}")
                print("You may need to configure AWS credentials and S3 bucket.")
        
        print("Database initialized successfully!")
    
    return app

if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Create the application
    application = create_app()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                Mental Health Hospital Management System       ║
    ║                                                              ║
    ║  🏥 Environment: {config_name.capitalize():<45} ║
    ║  🌐 Running on:  http://{host}:{port:<38} ║
    ║  🔒 Debug Mode:  {'Enabled' if debug else 'Disabled':<43} ║
    ║                                                              ║
    ║  📋 Features:                                                ║
    ║    • Staff Authentication & Authorization                    ║
    ║    • Patient Management System                               ║
    ║    • Electronic Case Notes with S3 Storage                  ║
    ║    • AI-Powered NLP Anomaly Detection                       ║
    ║    • Real-time Dashboard & Analytics                        ║
    ║    • HIPAA-Compliant Security Measures                      ║
    ║                                                              ║
    ║  🚀 Ready to serve healthcare professionals!                ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run the application
    application.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

