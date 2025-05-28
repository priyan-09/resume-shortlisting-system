from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from .models import db, Candidate, Education, Skill, JobDescription, Shortlist
from .utils.file_processor import upload_to_s3, get_s3_url
from .utils.parser import parse_resume
from .utils.shortlister import rank_candidates
from datetime import datetime
import tempfile

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('upload.html')

@bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save to temp file for processing
    file_extension = os.path.splitext(file.filename)[1][1:].lower()
    if file_extension not in ['pdf', 'docx', 'doc', 'txt']:
        return jsonify({'error': 'Unsupported file type'}), 400
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        file.save(temp_file.name)
        
        # Parse resume
        parsed_data = parse_resume(temp_file.name, file_extension)
        if not parsed_data:
            return jsonify({'error': 'Failed to parse resume'}), 500
        
        # Upload to S3
        file.seek(0)  # Reset file pointer
        file_key = upload_to_s3(file, secure_filename(file.filename))
        if not file_key:
            return jsonify({'error': 'Failed to upload to cloud storage'}), 500
        
        # Save to database
        candidate = Candidate(
            full_name=parsed_data['full_name'],
            email=parsed_data['email'],
            phone=parsed_data['phone'],
            location=parsed_data['location'],
            years_experience=parsed_data['years_experience'],
            resume_file_path=file_key,
            status='pending'
        )
        
        db.session.add(candidate)
        db.session.commit()
        
        # Add education
        for edu in parsed_data.get('education', []):
            education = Education(
                candidate_id=candidate.candidate_id,
                degree=edu.get('degree', ''),
                institution=edu.get('institution', ''),
                graduation_year=edu.get('graduation_year'),
                gpa=edu.get('gpa')
            )
            db.session.add(education)
        
        # Add skills
        for skill in parsed_data.get('skills', []):
            skill = Skill(
                candidate_id=candidate.candidate_id,
                skill_name=skill.get('name', ''),
                skill_category=skill.get('category', 'technical'),
                proficiency_level=skill.get('proficiency', 'intermediate')
            )
            db.session.add(skill)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resume processed successfully',
            'candidate_id': candidate.candidate_id
        }), 201

@bp.route('/candidates')
def list_candidates():
    candidates = Candidate.query.all()
    return render_template('dashboard.html', candidates=candidates)

@bp.route('/candidate/<int:candidate_id>')
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    educations = Education.query.filter_by(candidate_id=candidate_id).all()
    skills = Skill.query.filter_by(candidate_id=candidate_id).all()
    return render_template('candidate.html', candidate=candidate, educations=educations, skills=skills)

# routes.py - Update the shortlist endpoint
@bp.route('/shortlist', methods=['POST'])
def shortlist_candidates():
    job_description_text = request.form.get('job_description', '')
    if not job_description_text:
        return jsonify({'error': 'Job description is required'}), 400
    
    # Create a new job description record
    jd = JobDescription(description=job_description_text)
    db.session.add(jd)
    db.session.commit()
    
    # Get all candidates
    candidates = Candidate.query.all()
    candidates_data = []
    
    for candidate in candidates:
        educations = Education.query.filter_by(candidate_id=candidate.candidate_id).all()
        skills = Skill.query.filter_by(candidate_id=candidate.candidate_id).all()
        
        candidates_data.append({
            'candidate_id': candidate.candidate_id,
            'full_name': candidate.full_name,
            'years_experience': candidate.years_experience,
            'education': [{'degree': edu.degree} for edu in educations],
            'skills': [{'name': skill.skill_name} for skill in skills]
        })
    
    # Rank candidates
    top_candidates = rank_candidates(job_description_text, candidates_data)
    
    # Update status and create shortlist records
    for candidate in top_candidates:
        db_candidate = Candidate.query.get(candidate['candidate_id'])
        db_candidate.status = 'shortlisted'
        
        shortlist = Shortlist(
            job_description_id=jd.id,
            candidate_id=candidate['candidate_id'],
            score=candidate.get('score', 0)
        )
        db.session.add(shortlist)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Shortlisted {len(top_candidates)} candidates',
        'top_candidates': top_candidates,
        'job_description_id': jd.id
    })

# Add new route to view job descriptions
@bp.route('/job_descriptions')
def list_job_descriptions():
    job_descriptions = JobDescription.query.order_by(JobDescription.created_at.desc()).all()
    return render_template('job_descriptions.html', job_descriptions=job_descriptions)

# routes.py
@bp.route('/job_description/<int:jd_id>')
def job_description_detail(jd_id):
    job_description = JobDescription.query.get_or_404(jd_id)
    shortlisted_candidates = Shortlist.query.filter_by(job_description_id=jd_id)\
        .order_by(Shortlist.score.desc() if Shortlist.score is not None else None)\
        .all()
    return render_template('job_description.html', 
                         job_description=job_description,
                         shortlisted_candidates=shortlisted_candidates)