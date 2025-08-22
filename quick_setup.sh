#!/bin/bash

# Quick Setup Script for Mental Health Hospital Management System
# Pre-configured for your S3 bucket and RDS database

echo "🏥 Mental Health Hospital Management System - Quick Setup"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running on EC2
print_header "Checking environment..."
if curl -s --max-time 2 http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    print_status "Running on EC2 instance: $INSTANCE_ID"
else
    print_status "Running on local/non-EC2 environment"
fi

# Install system dependencies
print_header "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql-client-12 git curl

# Create virtual environment
print_header "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_header "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file with your configuration
print_header "Creating environment configuration..."
cat > .env << 'EOF'
# Flask Configuration
SECRET_KEY=hospital-management-secret-key-2024
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database Configuration (Your RDS Instance)
DATABASE_URL=postgresql://admin:Bayernmunich007$$@database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com:5432/hospital_db

# AWS Configuration (Your S3 Bucket)
AWS_ACCESS_KEY_ID=UPDATE_WITH_YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=UPDATE_WITH_YOUR_SECRET_KEY
AWS_S3_BUCKET=hosptialbuckets3
AWS_REGION=ap-southeast-2

# Application Settings
HOSPITAL_NAME=Mental Health Hospital
ANOMALY_THRESHOLD=0.3
MAX_CASE_NOTE_LENGTH=10000

# Security Settings
BCRYPT_LOG_ROUNDS=12
SESSION_TIMEOUT=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/application.log
EOF

print_status "Environment file created with your database and S3 configuration!"

# Create logs directory
mkdir -p logs
chmod 755 logs

# Set up database
print_header "Setting up database..."
python3 setup_database.py

# Create systemd service
print_header "Creating systemd service..."
sudo tee /etc/systemd/system/hospital-system.service > /dev/null << EOF
[Unit]
Description=Mental Health Hospital Management System
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hospital-system

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "🎉 Quick setup completed!"
echo "=========================="
echo ""
echo "📋 Your Configuration:"
echo "   Database: database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com"
echo "   S3 Bucket: hosptialbuckets3"
echo "   AWS Region: ap-southeast-2"
echo ""
echo "⚠️  IMPORTANT - Update AWS Credentials:"
echo "   1. Edit .env file: nano .env"
echo "   2. Replace 'UPDATE_WITH_YOUR_ACCESS_KEY' with your AWS Access Key ID"
echo "   3. Replace 'UPDATE_WITH_YOUR_SECRET_KEY' with your AWS Secret Access Key"
echo ""
echo "🚀 Start the application:"
echo "   sudo systemctl start hospital-system"
echo ""
echo "🌐 Access your application:"
echo "   http://$SERVER_IP:5000"
echo ""
echo "👥 Demo Login:"
echo "   Username: dr_smith"
echo "   Password: password123"
echo ""
echo "🔧 Useful Commands:"
echo "   sudo systemctl status hospital-system    # Check status"
echo "   sudo systemctl restart hospital-system   # Restart app"
echo "   sudo tail -f logs/application.log        # View logs"
echo "   python3 setup_database.py               # Re-setup database"
echo ""
print_warning "Don't forget to update your AWS credentials in .env file!"

