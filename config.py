import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hospital.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10))
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 3600))
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Security settings
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=SESSION_TIMEOUT)
    
    # Application settings
    HOSPITAL_NAME = os.environ.get('HOSPITAL_NAME', 'Mental Health Hospital')
    MAX_CASE_NOTE_LENGTH = int(os.environ.get('MAX_CASE_NOTE_LENGTH', 10000))
    ANOMALY_THRESHOLD = float(os.environ.get('ANOMALY_THRESHOLD', 0.3))
    NLP_MODEL_PATH = os.environ.get('NLP_MODEL_PATH', 'models/')
    
    # Email configuration (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/application.log')
    
    # Redis configuration (for caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.txt', '.pdf', '.doc', '.docx']
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hospital_dev.db'
    
    # Less strict security for development
    BCRYPT_LOG_ROUNDS = 4
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Create logs directory if it doesn't exist
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/hospital_dev.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Hospital Management System startup')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 1
    
    # Mock AWS services for testing
    AWS_ACCESS_KEY_ID = 'test-access-key'
    AWS_SECRET_ACCESS_KEY = 'test-secret-key'
    AWS_S3_BUCKET = 'test-bucket'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Ensure DATABASE_URL is set for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/hospital_prod'
    
    # Strong security settings
    BCRYPT_LOG_ROUNDS = 15
    
    # Require HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
        
        # Email errors to administrators
        if Config.MAIL_SERVER:
            import logging
            from logging.handlers import SMTPHandler
            
            credentials = None
            secure = None
            
            if Config.MAIL_USERNAME or Config.MAIL_PASSWORD:
                credentials = (Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            if Config.MAIL_USE_TLS:
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(Config.MAIL_SERVER, Config.MAIL_PORT),
                fromaddr='no-reply@' + Config.MAIL_SERVER,
                toaddrs=['admin@hospital.com'],
                subject='Hospital System Failure',
                credentials=credentials,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

