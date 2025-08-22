# Mental Health Hospital Management System - Deployment Guide

## 🚀 Quick Deployment on EC2

### Prerequisites
- EC2 instance running Ubuntu 20.04+
- RDS PostgreSQL database: `database-1.czgm060q6cf0.ap-southeast-2.rds.amazonaws.com`
- S3 bucket: `hosptialbuckets3`
- AWS credentials with S3 and RDS access

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd nlp-application
```

### 2. Run Deployment Script
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 3. Configure Environment
```bash
# Copy and edit environment file
cp env.production.example .env
nano .env

# Update these values:
# - SECRET_KEY (generate a secure key)
# - Database password in DATABASE_URL
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
```

### 4. Setup Database
```bash
python3 setup_database.py
```

### 5. Start Application
```bash
sudo systemctl start hospital-system
sudo systemctl enable hospital-system
```

### 6. Access Application
- URL: `http://your-ec2-ip:5000`
- Demo Login: `dr_smith` / `password123`

## 🔧 Manual Setup (Alternative)

### Install Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql-client
```

### Setup Application
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Application
```bash
# Development
python run.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:application
```

## 🔒 Security Notes

- Change default SECRET_KEY in production
- Use strong passwords for demo accounts
- Configure firewall rules (ports 22, 80, 443, 5000)
- Enable HTTPS with SSL certificates
- Restrict RDS access to your EC2 security group

## 📊 Infrastructure Details

- **Database**: PostgreSQL RDS in ap-southeast-2
- **Storage**: S3 bucket `hosptialbuckets3`
- **Compute**: EC2 instance (your choice)
- **Region**: Asia Pacific (Sydney)

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python3 -c "import psycopg2; conn = psycopg2.connect('your-database-url'); print('Connected!')"
```

### S3 Access Issues
```bash
# Test S3 access
aws s3 ls s3://hosptialbuckets3
```

### Application Logs
```bash
sudo journalctl -u hospital-system -f
tail -f logs/application.log
```

## 📞 Support
Check logs for errors and ensure all environment variables are properly set.
