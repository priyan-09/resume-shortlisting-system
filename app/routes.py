from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from .models import db, Candidate, Education, Skill, JobDescription, Shortlist
from .utils.file_processor import upload_to_s3, get_s3_url
from .utils.parser import parse_resume
from .utils.shortlister import rank_candidates
from datetime import datetime
import tempfile
from .config import Config

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
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file_path = temp_file.name
            file.save(temp_file.name)
            
            # Parse resume first to get email
            parsed_data = parse_resume(temp_file.name, file_extension)
            if not parsed_data:
                return jsonify({'error': 'Failed to parse resume'}), 500
            
            # Check if email already exists
            existing_candidate = Candidate.query.filter_by(email=parsed_data['email']).first()
            if existing_candidate:
                return jsonify({
                    'error': f'A candidate with email {parsed_data["email"]} already exists',
                    'existing_candidate_id': existing_candidate.candidate_id,
                    'existing_candidate_name': existing_candidate.full_name
                }), 409  # 409 Conflict status code
            
            # Only upload to S3 if candidate doesn't exist
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
                'candidate_id': candidate.candidate_id,
                'full_name': candidate.full_name,
                'email': candidate.email,
                'years_experience': candidate.years_experience
            }), 201
            
    except Exception as e:
        # If any error occurs, rollback the database session
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@bp.route('/candidates')
def list_candidates():
    candidates = Candidate.query.all()
    return render_template('dashboard.html', candidates=candidates)

@bp.route('/candidate/<int:candidate_id>')
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    educations = Education.query.filter_by(candidate_id=candidate_id).all()
    skills = Skill.query.filter_by(candidate_id=candidate_id).all()
    return render_template('candidate.html', 
                         candidate=candidate, 
                         educations=educations, 
                         skills=skills,
                         get_s3_url=get_s3_url)  # Add this line
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
    
    # Rank candidates and get top 10%
    top_candidates = rank_candidates(job_description_text, candidates_data, top_percent=10)
    
    # Update status and create shortlist records
    for candidate in top_candidates:
        db_candidate = Candidate.query.get(candidate['candidate_id'])
        db_candidate.status = 'shortlisted'
        
        shortlist = Shortlist(
            job_description_id=jd.id,
            candidate_id=candidate['candidate_id'],
            score=candidate['similarity_score']
        )
        db.session.add(shortlist)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Shortlisted top {len(top_candidates)} candidates (top 10%)',
        'top_candidates': top_candidates,
        'job_description_id': jd.id,
        'total_candidates': len(candidates_data),
        'shortlisted_count': len(top_candidates)
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


@bp.route('/candidate/<int:candidate_id>/delete', methods=['POST'])
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    try:
        # Delete from S3 first
        from .utils.file_processor import get_s3_client
        s3_client = get_s3_client()
        if s3_client and candidate.resume_file_path:
            try:
                s3_client.delete_object(
                    Bucket=Config.S3_BUCKET_NAME,
                    Key=candidate.resume_file_path
                )
            except Exception as e:
                logger.error(f"Error deleting resume from S3: {e}")
                # Continue with DB deletion even if S3 delete fails
        
        # Delete from database
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Candidate {candidate.full_name} deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to delete candidate: {str(e)}'
        }), 500

@bp.route('/job_description/<int:jd_id>/delete', methods=['POST'])
def delete_job_description(jd_id):
    jd = JobDescription.query.get_or_404(jd_id)
    
    try:
        # First delete all associated shortlist records
        Shortlist.query.filter_by(job_description_id=jd_id).delete()
        
        # Then delete the job description
        db.session.delete(jd)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Job Description #{jd_id} deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to delete job description: {str(e)}'
        }), 500