from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    candidate_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    resume_file_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    educations = db.relationship('Education', backref='candidate', lazy=True, cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='candidate', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        if 'email' in kwargs:
            kwargs['email'] = kwargs['email'].lower().strip()
        super().__init__(**kwargs)
    
    @classmethod
    def find_by_email(cls, email):
        """Find candidate by email (case-insensitive)"""
        return cls.query.filter(db.func.lower(cls.email) == email.lower().strip()).first()
    
    def __repr__(self):
        return f'<Candidate {self.full_name} ({self.email})>'

class Education(db.Model):
    __tablename__ = 'education'
    
    education_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    degree = db.Column(db.String(100))
    institution = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Numeric(3, 2))

class Skill(db.Model):
    __tablename__ = 'skills'
    
    skill_id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    skill_name = db.Column(db.String(100))
    skill_category = db.Column(db.String(20))
    proficiency_level = db.Column(db.String(20))


class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    
    shortlisted_candidates = db.relationship('Shortlist', backref='job_description', lazy=True)

class Shortlist(db.Model):
    __tablename__ = 'shortlists'
    
    id = db.Column(db.Integer, primary_key=True)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    score = db.Column(db.Float)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    
    candidate = db.relationship('Candidate', backref='shortlists')