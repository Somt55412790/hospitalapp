from datetime import datetime, timedelta, date
import random
import uuid
from app import Staff, Patient, CaseNote
import boto3

def create_dummy_staff(db):
    """Create dummy staff members for testing"""
    
    staff_data = [
        {
            'username': 'dr_smith',
            'email': 'dr.smith@mentalhealthhospital.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'job_title': 'Psychiatrist',
            'department': 'Psychiatry'
        },
        {
            'username': 'nurse_johnson',
            'email': 'sarah.johnson@mentalhealthhospital.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'job_title': 'Registered Nurse',
            'department': 'Inpatient Care'
        },
        {
            'username': 'therapist_brown',
            'email': 'michael.brown@mentalhealthhospital.com',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'job_title': 'Clinical Therapist',
            'department': 'Therapy Services'
        },
        {
            'username': 'social_worker_davis',
            'email': 'lisa.davis@mentalhealthhospital.com',
            'first_name': 'Lisa',
            'last_name': 'Davis',
            'job_title': 'Social Worker',
            'department': 'Social Services'
        },
        {
            'username': 'dr_wilson',
            'email': 'robert.wilson@mentalhealthhospital.com',
            'first_name': 'Robert',
            'last_name': 'Wilson',
            'job_title': 'Clinical Psychologist',
            'department': 'Psychology'
        },
        {
            'username': 'nurse_garcia',
            'email': 'maria.garcia@mentalhealthhospital.com',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'job_title': 'Licensed Practical Nurse',
            'department': 'Outpatient Care'
        },
        {
            'username': 'counselor_lee',
            'email': 'david.lee@mentalhealthhospital.com',
            'first_name': 'David',
            'last_name': 'Lee',
            'job_title': 'Mental Health Counselor',
            'department': 'Counseling Services'
        },
        {
            'username': 'admin_taylor',
            'email': 'jennifer.taylor@mentalhealthhospital.com',
            'first_name': 'Jennifer',
            'last_name': 'Taylor',
            'job_title': 'Administrative Coordinator',
            'department': 'Administration'
        },
        {
            'username': 'therapist_anderson',
            'email': 'james.anderson@mentalhealthhospital.com',
            'first_name': 'James',
            'last_name': 'Anderson',
            'job_title': 'Occupational Therapist',
            'department': 'Rehabilitation Services'
        },
        {
            'username': 'nurse_martinez',
            'email': 'ana.martinez@mentalhealthhospital.com',
            'first_name': 'Ana',
            'last_name': 'Martinez',
            'job_title': 'Psychiatric Nurse',
            'department': 'Acute Care'
        },
        {
            'username': 'dr_white',
            'email': 'patricia.white@mentalhealthhospital.com',
            'first_name': 'Patricia',
            'last_name': 'White',
            'job_title': 'Psychiatrist',
            'department': 'Emergency Services'
        },
        {
            'username': 'case_manager_clark',
            'email': 'thomas.clark@mentalhealthhospital.com',
            'first_name': 'Thomas',
            'last_name': 'Clark',
            'job_title': 'Case Manager',
            'department': 'Case Management'
        },
        {
            'username': 'therapist_lewis',
            'email': 'michelle.lewis@mentalhealthhospital.com',
            'first_name': 'Michelle',
            'last_name': 'Lewis',
            'job_title': 'Art Therapist',
            'department': 'Creative Therapies'
        },
        {
            'username': 'pharmacist_walker',
            'email': 'kevin.walker@mentalhealthhospital.com',
            'first_name': 'Kevin',
            'last_name': 'Walker',
            'job_title': 'Clinical Pharmacist',
            'department': 'Pharmacy'
        },
        {
            'username': 'supervisor_hall',
            'email': 'nancy.hall@mentalhealthhospital.com',
            'first_name': 'Nancy',
            'last_name': 'Hall',
            'job_title': 'Nursing Supervisor',
            'department': 'Nursing Administration'
        },
        {
            'username': 'resident_young',
            'email': 'daniel.young@mentalhealthhospital.com',
            'first_name': 'Daniel',
            'last_name': 'Young',
            'job_title': 'Psychiatric Resident',
            'department': 'Psychiatry'
        },
        {
            'username': 'tech_king',
            'email': 'stephanie.king@mentalhealthhospital.com',
            'first_name': 'Stephanie',
            'last_name': 'King',
            'job_title': 'Mental Health Technician',
            'department': 'Patient Care'
        },
        {
            'username': 'director_wright',
            'email': 'charles.wright@mentalhealthhospital.com',
            'first_name': 'Charles',
            'last_name': 'Wright',
            'job_title': 'Clinical Director',
            'department': 'Administration'
        }
    ]
    
    for staff_info in staff_data:
        staff = Staff(
            username=staff_info['username'],
            email=staff_info['email'],
            first_name=staff_info['first_name'],
            last_name=staff_info['last_name'],
            job_title=staff_info['job_title'],
            department=staff_info['department']
        )
        staff.set_password('password123')  # Default password for testing
        db.session.add(staff)
    
    db.session.commit()
    print(f"Created {len(staff_data)} dummy staff members")

def create_dummy_patients(db):
    """Create dummy patients for testing"""
    
    patient_data = [
        {
            'first_name': 'Alice',
            'last_name': 'Cooper',
            'date_of_birth': date(1985, 3, 15),
            'medical_record_number': 'MRN001001',
            'admission_date': datetime.now() - timedelta(days=30),
            'status': 'Active'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'date_of_birth': date(1978, 7, 22),
            'medical_record_number': 'MRN001002',
            'admission_date': datetime.now() - timedelta(days=45),
            'status': 'Active'
        },
        {
            'first_name': 'Carol',
            'last_name': 'Williams',
            'date_of_birth': date(1990, 11, 8),
            'medical_record_number': 'MRN001003',
            'admission_date': datetime.now() - timedelta(days=15),
            'status': 'Active'
        },
        {
            'first_name': 'David',
            'last_name': 'Brown',
            'date_of_birth': date(1982, 5, 30),
            'medical_record_number': 'MRN001004',
            'admission_date': datetime.now() - timedelta(days=60),
            'discharge_date': datetime.now() - timedelta(days=10),
            'status': 'Discharged'
        },
        {
            'first_name': 'Emma',
            'last_name': 'Davis',
            'date_of_birth': date(1995, 9, 12),
            'medical_record_number': 'MRN001005',
            'admission_date': datetime.now() - timedelta(days=20),
            'status': 'Active'
        },
        {
            'first_name': 'Frank',
            'last_name': 'Miller',
            'date_of_birth': date(1970, 12, 3),
            'medical_record_number': 'MRN001006',
            'admission_date': datetime.now() - timedelta(days=35),
            'status': 'Active'
        },
        {
            'first_name': 'Grace',
            'last_name': 'Wilson',
            'date_of_birth': date(1988, 4, 18),
            'medical_record_number': 'MRN001007',
            'admission_date': datetime.now() - timedelta(days=25),
            'status': 'Active'
        },
        {
            'first_name': 'Henry',
            'last_name': 'Moore',
            'date_of_birth': date(1975, 8, 27),
            'medical_record_number': 'MRN001008',
            'admission_date': datetime.now() - timedelta(days=50),
            'status': 'Active'
        },
        {
            'first_name': 'Iris',
            'last_name': 'Taylor',
            'date_of_birth': date(1992, 1, 14),
            'medical_record_number': 'MRN001009',
            'admission_date': datetime.now() - timedelta(days=12),
            'status': 'Active'
        },
        {
            'first_name': 'Jack',
            'last_name': 'Anderson',
            'date_of_birth': date(1980, 6, 9),
            'medical_record_number': 'MRN001010',
            'admission_date': datetime.now() - timedelta(days=40),
            'status': 'Active'
        }
    ]
    
    for patient_info in patient_data:
        patient = Patient(**patient_info)
        db.session.add(patient)
    
    db.session.commit()
    print(f"Created {len(patient_data)} dummy patients")

def create_dummy_case_notes(db, s3_client, bucket_name):
    """Create dummy case notes and upload to S3"""
    
    # Get all staff and patients
    staff_members = Staff.query.all()
    patients = Patient.query.all()
    
    if not staff_members or not patients:
        print("No staff or patients found. Please create them first.")
        return
    
    # Sample case note templates
    note_templates = {
        'Assessment': [
            "Patient presents with symptoms of {condition}. Mental status examination reveals {findings}. Current medication regimen includes {medications}. Patient reports {mood_description} mood and {sleep_pattern} sleep patterns. Cognitive function appears {cognitive_status}. Recommend continuing current treatment plan with {recommendations}.",
            "Initial assessment completed. Patient demonstrates {behavior_patterns} behavior patterns. Family history significant for {family_history}. Current stressors include {stressors}. Treatment goals established focusing on {treatment_goals}. Patient appears motivated for treatment.",
            "Comprehensive psychiatric evaluation conducted. Patient exhibits {symptoms} symptoms consistent with {diagnosis}. Previous treatment history includes {previous_treatment}. Current functioning level is {functioning_level}. Prognosis is {prognosis} with appropriate treatment."
        ],
        'Progress': [
            "Patient shows {progress_level} progress since last assessment. Medication compliance is {compliance_level}. Side effects reported include {side_effects}. Therapeutic alliance is {alliance_strength}. Patient reports {subjective_improvement} in symptoms. Plan to {future_plan}.",
            "Weekly progress review completed. Patient's mood has been {mood_trend} over the past week. Participation in group therapy has been {participation_level}. Sleep quality is {sleep_quality}. Appetite changes noted: {appetite_changes}. Continue current interventions.",
            "Progress note: Patient demonstrates {skill_development} in coping skills. Stress management techniques are being {technique_usage}. Social interactions have {social_progress}. Family involvement is {family_involvement}. Next session scheduled for {next_session}."
        ],
        'Treatment': [
            "Treatment session focused on {therapy_focus}. Patient engaged in {therapeutic_activities}. Breakthrough achieved in {breakthrough_area}. Homework assigned: {homework}. Patient's insight has {insight_development}. Session duration: {session_length} minutes.",
            "Individual therapy session conducted. Discussed {discussion_topics}. Patient demonstrated {emotional_regulation} emotional regulation. Coping strategies reviewed and {strategy_effectiveness}. Plan to introduce {new_interventions} in next session.",
            "Group therapy participation noted. Patient contributed {group_participation} to group discussions. Peer interactions were {peer_interactions}. Therapeutic exercises completed with {exercise_success}. Group dynamics observed as {group_dynamics}."
        ],
        'Medication': [
            "Medication review completed. Current regimen: {current_medications}. Efficacy assessment: {medication_efficacy}. Side effect profile: {side_effect_profile}. Laboratory results: {lab_results}. Dosage adjustments: {dosage_changes}. Next review scheduled for {next_review}.",
            "Psychiatric consultation for medication management. Patient reports {medication_response} response to current medications. Compliance assessed as {compliance_assessment}. Drug interactions reviewed: {drug_interactions}. Recommendations: {medication_recommendations}.",
            "Medication monitoring visit. Vital signs stable: {vital_signs}. Mood stabilization noted: {mood_stability}. Cognitive effects: {cognitive_effects}. Patient education provided regarding {patient_education}. Follow-up in {followup_timeframe}."
        ],
        'Discharge': [
            "Discharge planning initiated. Patient has met {discharge_criteria} discharge criteria. Community resources arranged: {community_resources}. Medication supply: {medication_supply}. Follow-up appointments: {followup_appointments}. Emergency contact information provided.",
            "Discharge summary: Patient admitted for {admission_reason}. Treatment goals achieved: {goals_achieved}. Remaining challenges: {remaining_challenges}. Aftercare plan includes {aftercare_plan}. Family education completed on {family_education_topics}.",
            "Patient ready for discharge to {discharge_destination}. Significant improvements noted in {improvement_areas}. Continuing care arrangements: {continuing_care}. Risk assessment: {risk_level}. Discharge medications: {discharge_medications}."
        ]
    }
    
    # Possible values for template variables
    template_values = {
        'condition': ['anxiety', 'depression', 'bipolar disorder', 'PTSD', 'adjustment disorder'],
        'findings': ['flat affect', 'elevated mood', 'anxious presentation', 'normal thought process', 'mild cognitive impairment'],
        'medications': ['sertraline 50mg', 'lithium 300mg', 'quetiapine 100mg', 'lorazepam 1mg PRN', 'aripiprazole 10mg'],
        'mood_description': ['depressed', 'anxious', 'stable', 'elevated', 'irritable'],
        'sleep_pattern': ['disturbed', 'improved', 'normal', 'fragmented', 'excessive'],
        'cognitive_status': ['intact', 'mildly impaired', 'within normal limits', 'improved', 'fluctuating'],
        'recommendations': ['medication adjustment', 'increased therapy frequency', 'family therapy', 'group therapy participation'],
        'progress_level': ['good', 'moderate', 'minimal', 'significant', 'steady'],
        'compliance_level': ['excellent', 'good', 'fair', 'poor', 'variable'],
        'side_effects': ['none reported', 'mild drowsiness', 'dry mouth', 'weight gain', 'nausea'],
        'alliance_strength': ['strong', 'developing', 'good', 'needs improvement', 'excellent'],
        'therapy_focus': ['coping skills', 'trauma processing', 'behavioral activation', 'cognitive restructuring', 'mindfulness'],
        'session_length': ['45', '50', '60', '30', '90']
    }
    
    note_types = list(note_templates.keys())
    notes_created = 0
    
    # Create case notes for each patient
    for patient in patients:
        # Create 5-8 notes per patient
        num_notes = random.randint(5, 8)
        
        for i in range(num_notes):
            # Select random staff member and note type
            staff_member = random.choice(staff_members)
            note_type = random.choice(note_types)
            
            # Select random template and fill variables
            template = random.choice(note_templates[note_type])
            
            # Fill template with random values
            filled_template = template
            for var_name, var_values in template_values.items():
                if f'{{{var_name}}}' in filled_template:
                    filled_template = filled_template.replace(f'{{{var_name}}}', random.choice(var_values))
            
            # Remove any unfilled template variables
            import re
            filled_template = re.sub(r'\{[^}]+\}', '[details]', filled_template)
            
            # Create case note
            case_note = CaseNote(
                patient_id=patient.patient_id,
                staff_id=staff_member.staff_id,
                note_type=note_type,
                title=f"{note_type} - {datetime.now().strftime('%Y-%m-%d')}",
                content=filled_template,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Upload to S3 with comprehensive metadata
            try:
                # Create structured file path
                file_key = f"case_notes/{patient.patient_id}/{case_note.created_at.strftime('%Y/%m/%d')}/{uuid.uuid4().hex}.txt"
                
                # Prepare comprehensive metadata
                s3_metadata = {
                    'patient_id': str(patient.patient_id),
                    'patient_mrn': patient.medical_record_number,
                    'patient_name': f"{patient.first_name} {patient.last_name}",
                    'staff_id': str(staff_member.staff_id),
                    'staff_name': f"{staff_member.first_name} {staff_member.last_name}",
                    'staff_title': staff_member.job_title,
                    'staff_department': staff_member.department or 'unknown',
                    'note_type': note_type,
                    'note_title': case_note.title,
                    'created_at': case_note.created_at.isoformat(),
                    'content_length': str(len(filled_template)),
                    'hospital_name': 'Mental Health Hospital',
                    'system_version': '1.0.0'
                }
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=file_key,
                    Body=filled_template.encode('utf-8'),
                    ContentType='text/plain; charset=utf-8',
                    Metadata=s3_metadata,
                    ServerSideEncryption='AES256'  # Enable encryption
                )
                
                case_note.s3_file_key = file_key
                case_note.s3_bucket = bucket_name
                case_note.file_size = len(filled_template.encode('utf-8'))
                case_note.file_type = 'text/plain'
                
            except Exception as e:
                print(f"Warning: Could not upload to S3: {e}")
                # Continue without S3 upload
            
            db.session.add(case_note)
            notes_created += 1
    
    # Create some anomalous notes for testing NLP detection
    anomalous_templates = [
        "EMERGENCY: Patient became extremely agitated and required immediate intervention. Security called. Patient restrained. Medication administered stat. Incident report filed. Family notified.",
        "CRITICAL INCIDENT: Patient found unresponsive in room. Code blue called. Vital signs unstable. Emergency medical team responded. Patient transferred to medical unit.",
        "UNUSUAL BEHAVIOR: Patient reported hearing voices commanding self-harm. Placed on 1:1 observation. Psychiatrist notified immediately. Safety plan initiated.",
        "MEDICATION ERROR: Wrong medication administered to patient. Error discovered during shift change. Patient monitored for adverse reactions. Incident reported to pharmacy and administration.",
        "ELOPEMENT ATTEMPT: Patient attempted to leave unit without authorization. Found in parking lot. Returned safely to unit. Security measures reviewed."
    ]
    
    # Add a few anomalous notes
    for i in range(3):
        patient = random.choice(patients)
        staff_member = random.choice(staff_members)
        anomalous_content = random.choice(anomalous_templates)
        
        case_note = CaseNote(
            patient_id=patient.patient_id,
            staff_id=staff_member.staff_id,
            note_type='Incident',
            title=f"Incident Report - {datetime.now().strftime('%Y-%m-%d')}",
            content=anomalous_content,
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            is_flagged=True,  # Pre-flag these as anomalous
            anomaly_score=0.85
        )
        
        try:
            file_key = f"case_notes/{patient.patient_id}/{case_note.created_at.strftime('%Y/%m/%d')}/{uuid.uuid4().hex}.txt"
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=anomalous_content.encode('utf-8'),
                ContentType='text/plain',
                Metadata={
                    'patient_id': str(patient.patient_id),
                    'staff_id': str(staff_member.staff_id),
                    'note_type': 'Incident',
                    'title': case_note.title,
                    'created_at': case_note.created_at.isoformat(),
                    'is_anomalous': 'true'
                }
            )
            
            case_note.s3_file_key = file_key
            case_note.s3_bucket = bucket_name
            case_note.file_size = len(anomalous_content.encode('utf-8'))
            case_note.file_type = 'text/plain'
            
        except Exception as e:
            print(f"Warning: Could not upload anomalous note to S3: {e}")
        
        db.session.add(case_note)
        notes_created += 1
    
    db.session.commit()
    print(f"Created {notes_created} dummy case notes (including {3} anomalous ones)")

if __name__ == "__main__":
    print("This module contains functions to create dummy data.")
    print("Import and call create_dummy_staff(), create_dummy_patients(), and create_dummy_case_notes() functions.")
