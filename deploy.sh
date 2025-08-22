#!/bin/bash

# Mental Health Hospital Management System - Deployment Script
# This script automates the deployment process on AWS EC2

echo "🏥 Mental Health Hospital Management System - Deployment Script"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_header "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_header "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git curl

# Install Node.js (for any future frontend build tools)
print_header "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
APP_DIR="/var/www/hospital-system"
print_header "Setting up application directory at $APP_DIR..."

if [ -d "$APP_DIR" ]; then
    print_warning "Application directory already exists. Backing up..."
    sudo mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

sudo mkdir -p "$APP_DIR"
sudo chown $USER:$USER "$APP_DIR"

# Clone or copy application files
if [ -d ".git" ]; then
    print_status "Git repository detected, cloning to deployment directory..."
    git clone . "$APP_DIR"
else
    print_status "Copying application files..."
    cp -r . "$APP_DIR"
fi

cd "$APP_DIR"

# Create virtual environment
print_header "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_header "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL client (for connecting to RDS)
print_header "Installing PostgreSQL client for RDS connection..."
sudo apt install -y postgresql-client-common postgresql-client-12

print_status "PostgreSQL client installed. Using external RDS database:"
print_status "Database endpoint: database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com"
print_status "Database user: admin"
print_status "S3 Bucket: hosptialbuckets3"
print_status "AWS Region: ap-southeast-2"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_header "Creating environment configuration..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database Configuration (Your RDS Instance)
DATABASE_URL=postgresql://admin:Bayernmunich007\$\$@database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com:5432/hospital_db

# AWS Configuration (Your S3 Bucket - UPDATE ACCESS KEYS)
AWS_ACCESS_KEY_ID=your-aws-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here
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
    print_warning "IMPORTANT: Please update the AWS Access Key ID and Secret Access Key in .env file!"
    print_warning "Your S3 bucket (hosptialbuckets3) and RDS database are already configured."
fi

# Create logs directory
mkdir -p logs
chmod 755 logs

# Initialize database
print_header "Initializing database..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"

# Create Gunicorn configuration
print_header "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << EOF
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "$USER"
group = "$USER"
pidfile = "/var/www/hospital-system/gunicorn.pid"
accesslog = "/var/www/hospital-system/logs/gunicorn-access.log"
errorlog = "/var/www/hospital-system/logs/gunicorn-error.log"
loglevel = "info"
EOF

# Create systemd service file
print_header "Creating systemd service..."
sudo tee /etc/systemd/system/hospital-system.service > /dev/null << EOF
[Unit]
Description=Mental Health Hospital Management System
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
print_header "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/hospital-system > /dev/null << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/hospital-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_header "Testing Nginx configuration..."
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Create SSL certificate (Let's Encrypt) - Optional
read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_header "Setting up SSL certificate..."
    sudo apt install -y certbot python3-certbot-nginx
    read -p "Enter your domain name: " domain_name
    sudo certbot --nginx -d "$domain_name" --non-interactive --agree-tos --email "admin@$domain_name"
fi

# Set proper permissions
print_header "Setting file permissions..."
sudo chown -R $USER:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod -R 775 "$APP_DIR/logs"

# Start and enable services
print_header "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable hospital-system
sudo systemctl start hospital-system
sudo systemctl enable nginx
sudo systemctl restart nginx

# Create backup script
print_header "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
# Backup script for Hospital Management System

BACKUP_DIR="/var/backups/hospital-system"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
sudo -u postgres pg_dump hospital_prod > "$BACKUP_DIR/database_$DATE.sql"

# Backup application files (excluding venv and logs)
tar -czf "$BACKUP_DIR/application_$DATE.tar.gz" \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /var/www/hospital-system

# Keep only last 7 days of backups
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Setup cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -

# Create monitoring script
print_header "Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script

APP_URL="http://localhost"
LOG_FILE="/var/www/hospital-system/logs/monitor.log"

# Check if application is responding
if curl -f -s "$APP_URL" > /dev/null; then
    echo "$(date): Application is running" >> "$LOG_FILE"
else
    echo "$(date): Application is down - restarting" >> "$LOG_FILE"
    sudo systemctl restart hospital-system
    sleep 10
    if curl -f -s "$APP_URL" > /dev/null; then
        echo "$(date): Application restarted successfully" >> "$LOG_FILE"
    else
        echo "$(date): Application restart failed" >> "$LOG_FILE"
    fi
fi
EOF

chmod +x monitor.sh

# Setup cron job for monitoring (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -

# Final status check
print_header "Checking deployment status..."
sleep 5

if systemctl is-active --quiet hospital-system; then
    print_status "✅ Hospital Management System service is running"
else
    print_error "❌ Hospital Management System service is not running"
    sudo systemctl status hospital-system
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx is not running"
    sudo systemctl status nginx
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "🎉 Deployment completed successfully!"
echo "================================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Update AWS credentials in $APP_DIR/.env"
echo "2. Create and configure your S3 bucket"
echo "3. Update your domain name in Nginx configuration if needed"
echo ""
echo "🌐 Access your application:"
echo "   http://$SERVER_IP"
echo ""
echo "👥 Demo Login Credentials:"
echo "   Username: dr_smith"
echo "   Password: password123"
echo ""
echo "📁 Important Files:"
echo "   Application: $APP_DIR"
echo "   Configuration: $APP_DIR/.env"
echo "   Logs: $APP_DIR/logs/"
echo "   Nginx Config: /etc/nginx/sites-available/hospital-system"
echo ""
echo "🔧 Useful Commands:"
echo "   sudo systemctl status hospital-system"
echo "   sudo systemctl restart hospital-system"
echo "   sudo systemctl restart nginx"
echo "   sudo tail -f $APP_DIR/logs/gunicorn-error.log"
echo ""
echo "⚠️  Remember to:"
echo "   - Configure AWS S3 credentials"
echo "   - Set up SSL certificate for production"
echo "   - Configure firewall rules"
echo "   - Set up regular backups"
echo "   - Monitor system performance"
echo ""
print_status "Deployment script completed!"
EOF

chmod +x deploy.sh
