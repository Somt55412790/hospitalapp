
# Mental Health Hospital Management System

A web-based hospital management system for mental health facilities, featuring AI-powered NLP anomaly detection, secure cloud storage, and modern healthcare workflow management.

## Project Structure

```
app.py
config.py
deploy.sh
DEPLOYMENT.md
env.production.example
nlp_processor.py
README.md
requirements.txt
run.py
templates/
    add_case_note.html
    anomalies.html
    base.html
    case_notes.html
    client_notes.html
    client_search.html
    dashboard.html
    index.html
    login.html
    patients.html
    register.html
    view_note.html
wsgi.py
```

## About
- AI-powered anomaly detection for case notes
- Secure authentication and patient management
- Cloud storage integration (AWS S3)
- Modern, responsive web interface

For deployment, all cloud infrastructure is managed externally.
git clone https://github.com/your-username/mental-health-hospital-system.git
cd mental-health-hospital-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Set Up AWS S3 Bucket
1. Create an S3 bucket in your AWS account
2. Configure IAM user with S3 access permissions
3. Add credentials to your `.env` file

### 6. Initialize Database
```bash
python run.py
```

The system will automatically create database tables and populate with dummy data for testing.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# Application Settings
HOSPITAL_NAME=Mental Health Hospital
ANOMALY_THRESHOLD=0.3
```

### Database Setup

#### Development (SQLite)
```bash
# SQLite database will be created automatically
DATABASE_URL=sqlite:///hospital.db
```

#### Production (PostgreSQL)
```bash
# Install PostgreSQL and create database
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb hospital_db
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db
```

## 🚀 Deployment on AWS EC2

### 1. Launch EC2 Instance
- Choose Ubuntu 20.04 LTS AMI
- Instance type: t3.medium or larger
- Configure security groups (HTTP, HTTPS, SSH)
- Create or use existing key pair

### 2. Connect to EC2 Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Install System Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

### 4. Clone and Setup Application
```bash
git clone https://github.com/your-username/mental-health-hospital-system.git
cd mental-health-hospital-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
# Create production environment file
cp .env.example .env
# Edit with production values
nano .env
```

### 6. Setup Database
```bash
sudo -u postgres createdb hospital_prod
sudo -u postgres createuser hospital_user
sudo -u postgres psql -c "ALTER USER hospital_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hospital_prod TO hospital_user;"
```

### 7. Run with Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 wsgi:application
```

### 8. Configure Nginx (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 👥 Demo Credentials

The system comes with pre-populated demo data:

### Staff Accounts
- **Psychiatrist**: `dr_smith` / `password123`
- **Nurse**: `nurse_johnson` / `password123`
- **Therapist**: `therapist_brown` / `password123`
- **Social Worker**: `social_worker_davis` / `password123`

### Features to Test
1. **Login** with any demo account
2. **Dashboard** - View system statistics and recent activity
3. **Case Notes** - Create, view, and manage patient notes
4. **Patients** - Browse patient directory
5. **Anomalies** - Review AI-flagged unusual notes
6. **NLP Analysis** - Test anomaly detection system

## 🧠 NLP Anomaly Detection

The system uses advanced machine learning to detect unusual patterns in case notes:

### Detection Methods
- **Content Similarity Analysis** - Compares note content with patient's historical notes
- **Length Deviation Detection** - Identifies unusually long or short notes
- **Vocabulary Analysis** - Detects unusual terminology or writing style changes
- **Pattern Recognition** - Identifies potential data entry errors or crisis situations

### Anomaly Scoring
- **High (0.7+)**: Immediate review required
- **Medium (0.4-0.7)**: Attention recommended
- **Low (0.0-0.4)**: Minor variations, monitoring suggested

### Use Cases
- **Crisis Detection** - Automatic flagging of emergency situations
- **Data Quality** - Identification of potential entry errors
- **Consistency Monitoring** - Detection of unusual documentation patterns
- **Training Support** - Assistance for new staff members

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask App      │    │   PostgreSQL    │
│   (Bootstrap)   │◄──►│   (Python)       │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AWS S3 Bucket  │
                       │   (File Storage) │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  NLP Processor   │
                       │  (scikit-learn)  │
                       └──────────────────┘
```

## 🔒 Security Considerations

### Data Protection
- All passwords are hashed using bcrypt
- Session data is encrypted and expires automatically
- Database connections use SSL in production
- S3 files are encrypted at rest and in transit

### Access Control
- Role-based permissions for different staff types
- Session timeout protection
- CSRF protection on all forms
- SQL injection prevention through ORM

### Compliance
- HIPAA-compliant data handling procedures
- Audit logging for all data access
- Secure file storage with metadata separation
- Regular security updates and monitoring

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Test Coverage
```bash
pip install pytest-cov
python -m pytest --cov=app tests/
```

### Load Testing
```bash
pip install locust
locust -f tests/load_test.py --host=http://localhost:5000
```

## 📝 API Documentation

The system provides RESTful endpoints for integration:

### Authentication
- `POST /api/login` - Staff authentication
- `POST /api/logout` - Session termination

### Case Notes
- `GET /api/notes` - List case notes
- `POST /api/notes` - Create new note
- `GET /api/notes/<id>` - Get specific note
- `PUT /api/notes/<id>` - Update note
- `DELETE /api/notes/<id>` - Delete note

### Anomaly Detection
- `POST /api/analyze/<note_id>` - Run anomaly analysis
- `GET /api/anomalies` - List flagged notes
- `PUT /api/anomalies/<id>/resolve` - Mark as resolved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation for API changes
- Ensure HIPAA compliance for health data features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@hospital-system.com
- Documentation: [Wiki](https://github.com/your-username/mental-health-hospital-system/wiki)

## 🙏 Acknowledgments

- **Flask Framework** - Web application foundation
- **scikit-learn** - Machine learning capabilities
- **AWS Services** - Cloud infrastructure
- **Bootstrap** - UI framework
- **Font Awesome** - Icon library
- **Mental Health Community** - Requirements and feedback

---

**⚠️ Important**: This system handles sensitive health information. Ensure proper security measures, regular backups, and compliance with local healthcare regulations before production use.

