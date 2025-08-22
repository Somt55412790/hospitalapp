from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import json
import uuid
from nlp_processor import NLPAnomalyDetector

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# AWS Configuration
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['AWS_S3_BUCKET'] = os.environ.get('AWS_S3_BUCKET')
app.config['AWS_REGION'] = os.environ.get('AWS_REGION', 'us-east-1')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    region_name=app.config['AWS_REGION']
)

# Initialize NLP processor
nlp_detector = NLPAnomalyDetector()

# Database Models
class Staff(UserMixin, db.Model):
    __tablename__ = 'staff'
    
    staff_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to case notes
    case_notes = db.relationship('CaseNote', backref='staff_member', lazy=True)
    
    def get_id(self):
        return str(self.staff_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Staff {self.username}>'

class Patient(db.Model):
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_record_number = db.Column(db.String(20), unique=True, nullable=False)
    admission_date = db.Column(db.DateTime, nullable=True)
    discharge_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to case notes
    case_notes = db.relationship('CaseNote', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.medical_record_number}>'

class CaseNote(db.Model):
    __tablename__ = 'case_notes'
    
    note_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    note_type = db.Column(db.String(50), nullable=False)  # Assessment, Progress, Treatment, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    s3_file_key = db.Column(db.String(500), nullable=True)  # S3 object key for file storage
    s3_bucket = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_flagged = db.Column(db.Boolean, default=False)  # For NLP anomaly detection
    anomaly_score = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<CaseNote {self.note_id}>'

@login_manager.user_loader
def load_user(user_id):
    return Staff.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        staff = Staff.query.filter_by(username=username).first()
        
        if staff and staff.check_password(password) and staff.is_active:
            login_user(staff)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        job_title = request.form['job_title']
        department = request.form.get('department', '')
        
        # Check if user already exists
        if Staff.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if Staff.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new staff member
        new_staff = Staff(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            department=department
        )
        new_staff.set_password(password)
        
        db.session.add(new_staff)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent case notes by current user
    recent_notes = CaseNote.query.filter_by(staff_id=current_user.staff_id)\
                                .order_by(CaseNote.created_at.desc())\
                                .limit(5).all()
    
    # Get statistics
    total_notes = CaseNote.query.filter_by(staff_id=current_user.staff_id).count()
    flagged_notes = CaseNote.query.filter_by(staff_id=current_user.staff_id, is_flagged=True).count()
    total_patients = Patient.query.count()
    
    return render_template('dashboard.html', 
                         recent_notes=recent_notes,
                         total_notes=total_notes,
                         flagged_notes=flagged_notes,
                         total_patients=total_patients)

@app.route('/case_notes')
@login_required
def case_notes():
    page = request.args.get('page', 1, type=int)
    notes = CaseNote.query.filter_by(staff_id=current_user.staff_id)\
                         .order_by(CaseNote.created_at.desc())\
                         .paginate(page=page, per_page=10, error_out=False)
    return render_template('case_notes.html', notes=notes)

@app.route('/add_case_note', methods=['GET', 'POST'])
@login_required
def add_case_note():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        note_type = request.form['note_type']
        title = request.form['title']
        content = request.form['content']
        
        # Create new case note with metadata
        case_note = CaseNote(
            patient_id=patient_id,
            staff_id=current_user.staff_id,
            note_type=note_type,
            title=title,
            content=content
        )
        
        # First save to database to get the note_id
        db.session.add(case_note)
        db.session.flush()  # This assigns the note_id without committing
        
        # Upload full content to S3 and store metadata in database
        try:
            s3_metadata = upload_case_note_to_s3_with_metadata(case_note, current_user)
            
            # Update case note with S3 metadata
            case_note.s3_file_key = s3_metadata['file_key']
            case_note.s3_bucket = s3_metadata['bucket']
            case_note.file_size = s3_metadata['file_size']
            case_note.file_type = s3_metadata['file_type']
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading to S3: {str(e)}', 'error')
            return render_template('add_case_note.html', patients=Patient.query.all())
        
        # Commit the transaction
        db.session.commit()
        
        # Run NLP anomaly detection asynchronously
        try:
            run_anomaly_detection(case_note.note_id)
            flash('Case note added successfully and uploaded to secure storage!', 'success')
        except Exception as e:
            flash(f'Note saved successfully, but anomaly detection encountered an issue: {str(e)}', 'warning')
        
        return redirect(url_for('case_notes'))
    
    patients = Patient.query.filter_by(status='Active').order_by(Patient.last_name, Patient.first_name).all()
    return render_template('add_case_note.html', patients=patients)

@app.route('/patients')
@login_required
def patients():
    page = request.args.get('page', 1, type=int)
    patients = Patient.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('patients.html', patients=patients)

@app.route('/anomalies')
@login_required
def anomalies():
    flagged_notes = CaseNote.query.filter_by(is_flagged=True)\
                                 .order_by(CaseNote.anomaly_score.desc()).all()
    return render_template('anomalies.html', flagged_notes=flagged_notes)

@app.route('/client_search')
@login_required
def client_search():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    if search_query:
        # Search patients by name, MRN, or patient ID
        patients = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search_query}%'),
                Patient.last_name.ilike(f'%{search_query}%'),
                Patient.medical_record_number.ilike(f'%{search_query}%'),
                db.func.concat(Patient.first_name, ' ', Patient.last_name).ilike(f'%{search_query}%')
            )
        ).order_by(Patient.last_name, Patient.first_name)\
         .paginate(page=page, per_page=10, error_out=False)
    else:
        patients = Patient.query.order_by(Patient.last_name, Patient.first_name)\
                               .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('client_search.html', patients=patients, search_query=search_query)

@app.route('/client_notes/<int:patient_id>')
@login_required
def client_notes(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    page = request.args.get('page', 1, type=int)
    note_type = request.args.get('note_type', '')
    staff_filter = request.args.get('staff_filter', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query for patient's case notes
    query = CaseNote.query.filter_by(patient_id=patient_id)
    
    # Apply filters
    if note_type:
        query = query.filter_by(note_type=note_type)
    
    if staff_filter == 'current':
        query = query.filter_by(staff_id=current_user.staff_id)
    elif staff_filter and staff_filter.isdigit():
        query = query.filter_by(staff_id=int(staff_filter))
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(CaseNote.created_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            to_date = to_date.replace(hour=23, minute=59, second=59)
            query = query.filter(CaseNote.created_at <= to_date)
        except ValueError:
            pass
    
    # Get paginated notes
    notes = query.order_by(CaseNote.created_at.desc())\
                 .paginate(page=page, per_page=10, error_out=False)
    
    # Get all staff who have written notes for this patient
    staff_list = db.session.query(Staff).join(CaseNote)\
                          .filter(CaseNote.patient_id == patient_id)\
                          .distinct().all()
    
    # Calculate statistics
    total_notes = CaseNote.query.filter_by(patient_id=patient_id).count()
    flagged_notes = CaseNote.query.filter_by(patient_id=patient_id, is_flagged=True).count()
    recent_notes = CaseNote.query.filter_by(patient_id=patient_id)\
                                .filter(CaseNote.created_at >= datetime.now() - timedelta(days=30))\
                                .count()
    
    return render_template('client_notes.html', 
                         patient=patient, 
                         notes=notes, 
                         staff_list=staff_list,
                         total_notes=total_notes,
                         flagged_notes=flagged_notes,
                         recent_notes=recent_notes)

@app.route('/view_note/<int:note_id>')
@login_required
def view_note(note_id):
    note = CaseNote.query.get_or_404(note_id)
    
    # Retrieve full content from S3 if available
    s3_content = None
    if note.s3_file_key and note.s3_bucket:
        try:
            s3_data = retrieve_case_note_from_s3(note.s3_file_key, note.s3_bucket)
            s3_content = s3_data['content']
        except Exception as e:
            flash(f'Could not retrieve full content from storage: {str(e)}', 'warning')
    
    # Get related notes for context (previous 3 notes for same patient)
    related_notes = CaseNote.query.filter(
        CaseNote.patient_id == note.patient_id,
        CaseNote.note_id != note.note_id,
        CaseNote.created_at < note.created_at
    ).order_by(CaseNote.created_at.desc()).limit(3).all()
    
    return render_template('view_note.html', 
                         note=note, 
                         s3_content=s3_content,
                         related_notes=related_notes)

@app.route('/api/search_patients')
@login_required
def api_search_patients():
    """API endpoint for patient search autocomplete"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    patients = Patient.query.filter(
        db.or_(
            Patient.first_name.ilike(f'%{query}%'),
            Patient.last_name.ilike(f'%{query}%'),
            Patient.medical_record_number.ilike(f'%{query}%'),
            db.func.concat(Patient.first_name, ' ', Patient.last_name).ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for patient in patients:
        results.append({
            'id': patient.patient_id,
            'name': f"{patient.first_name} {patient.last_name}",
            'mrn': patient.medical_record_number,
            'status': patient.status
        })
    
    return jsonify(results)

def upload_case_note_to_s3_with_metadata(case_note, staff_user):
    """Upload case note content to S3 with comprehensive metadata and return metadata dict"""
    # Create structured file path
    file_key = f"case_notes/{case_note.patient_id}/{datetime.now().strftime('%Y/%m/%d')}/{case_note.note_id}_{uuid.uuid4().hex}.txt"
    
    # Get patient information
    patient = Patient.query.get(case_note.patient_id)
    
    # Prepare comprehensive metadata
    s3_metadata = {
        'note_id': str(case_note.note_id),
        'patient_id': str(case_note.patient_id),
        'patient_mrn': patient.medical_record_number if patient else 'unknown',
        'patient_name': f"{patient.first_name} {patient.last_name}" if patient else 'unknown',
        'staff_id': str(case_note.staff_id),
        'staff_name': f"{staff_user.first_name} {staff_user.last_name}",
        'staff_title': staff_user.job_title,
        'staff_department': staff_user.department or 'unknown',
        'note_type': case_note.note_type,
        'note_title': case_note.title,
        'created_at': datetime.now().isoformat(),
        'content_length': str(len(case_note.content)),
        'hospital_name': app.config.get('HOSPITAL_NAME', 'Mental Health Hospital'),
        'system_version': '1.0.0'
    }
    
    try:
        # Upload to S3 with rich metadata
        s3_client.put_object(
            Bucket=app.config['AWS_S3_BUCKET'],
            Key=file_key,
            Body=case_note.content.encode('utf-8'),
            ContentType='text/plain; charset=utf-8',
            Metadata=s3_metadata,
            ServerSideEncryption='AES256',  # Enable encryption
            StorageClass='STANDARD'  # Can be changed to STANDARD_IA for cost optimization
        )
        
        # Return metadata for database storage
        return {
            'file_key': file_key,
            'bucket': app.config['AWS_S3_BUCKET'],
            'file_size': len(case_note.content.encode('utf-8')),
            'file_type': 'text/plain',
            'upload_timestamp': datetime.now().isoformat(),
            'staff_id': case_note.staff_id
        }
        
    except ClientError as e:
        raise Exception(f"Failed to upload to S3: {e}")

def retrieve_case_note_from_s3(s3_file_key, bucket_name):
    """Retrieve case note content from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        content = response['Body'].read().decode('utf-8')
        metadata = response.get('Metadata', {})
        
        return {
            'content': content,
            'metadata': metadata,
            'last_modified': response.get('LastModified'),
            'content_length': response.get('ContentLength')
        }
    except ClientError as e:
        raise Exception(f"Failed to retrieve from S3: {e}")

def run_anomaly_detection(note_id):
    """Run NLP anomaly detection on the case note"""
    case_note = CaseNote.query.get(note_id)
    if not case_note:
        return
    
    # Get the last 3 case notes for the same patient (excluding current one)
    previous_notes = CaseNote.query.filter(
        CaseNote.patient_id == case_note.patient_id,
        CaseNote.note_id != case_note.note_id
    ).order_by(CaseNote.created_at.desc()).limit(3).all()
    
    if len(previous_notes) < 2:  # Need at least 2 previous notes for comparison
        return
    
    # Extract content from previous notes
    previous_contents = [note.content for note in previous_notes]
    
    # Run anomaly detection
    is_anomaly, score = nlp_detector.detect_anomaly(case_note.content, previous_contents)
    
    # Update case note with results
    case_note.is_flagged = is_anomaly
    case_note.anomaly_score = score
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create dummy data if no staff exists
        if Staff.query.count() == 0:
            create_dummy_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_dummy_data():
    """Create dummy staff and patient data for testing"""
    from dummy_data import create_dummy_staff, create_dummy_patients, create_dummy_case_notes
    create_dummy_staff(db)
    create_dummy_patients(db)
    create_dummy_case_notes(db, s3_client, app.config['AWS_S3_BUCKET'])
