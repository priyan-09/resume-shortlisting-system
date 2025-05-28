import pdfplumber
from docx import Document
import spacy
import re
from datetime import datetime

nlp = spacy.load("en_core_web_lg")

def extract_text(file_path, file_extension):
    """Extract text from different file formats"""
    text = ""
    try:
        if file_extension == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif file_extension in ['docx', 'doc']:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:  # txt
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def extract_work_experience(text):
    """Extract work experience from resume text"""
    work_experiences = []
    
    # Look for common work experience patterns
    experience_patterns = [
        r'(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)(?=\n|•)',  # Title | Company | Date
        r'(.*?)\s+at\s+(.*?)\s+\((.*?)\)',  # Title at Company (Date)
    ]
    
    # Split text into lines and look for experience entries
    lines = text.split('\n')
    current_experience = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if line matches job title pattern (often in bold/caps or followed by company)
        for pattern in experience_patterns:
            match = re.search(pattern, line)
            if match:
                title, company, date_range = match.groups()
                
                # Extract responsibilities from following lines starting with •
                responsibilities = []
                for j in range(i + 1, min(i + 10, len(lines))):  # Look at next 10 lines
                    next_line = lines[j].strip()
                    if next_line.startswith('•'):
                        responsibilities.append(next_line[1:].strip())
                    elif next_line and not next_line.startswith('•') and len(responsibilities) > 0:
                        break
                
                work_experiences.append({
                    'title': title.strip(),
                    'company': company.strip(),
                    'date_range': date_range.strip(),
                    'description': responsibilities
                })
                break
    
    # If no matches found with patterns, try a different approach
    if not work_experiences:
        # Look for lines that might be job titles (followed by company info)
        job_sections = re.findall(
            r'((?:Senior |Junior |Lead )?(?:Software Engineer|Developer|Analyst|Manager|Director|Consultant)[^\n]*)\s*\|\s*([^\n]*)\s*\|\s*([^\n]*)',
            text, re.IGNORECASE
        )
        
        for title, company, date_range in job_sections:
            # Find responsibilities for this job
            responsibilities = []
            # Look for bullet points after this job entry
            job_section = text[text.find(title):text.find(title) + 500]  # Next 500 chars
            bullet_points = re.findall(r'•\s*([^\n•]+)', job_section)
            responsibilities = [point.strip() for point in bullet_points]
            
            work_experiences.append({
                'title': title.strip(),
                'company': company.strip(),
                'date_range': date_range.strip(),
                'description': responsibilities
            })
    
    return work_experiences

def extract_entities(text):
    """Extract entities using spaCy"""
    doc = nlp(text)
    
    # Extract entities
    entities = {
        'PERSON': [],
        'EMAIL': [],
        'PHONE': [],
        'ORG': [],
        'GPE': [],
        'DATE': [],
        'SKILL': []
    }
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # Improved email extraction
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    
    # Improved phone extraction - multiple patterns
    phone_patterns = [
        r'\+1-\d{3}-\d{4}',  # +1-555-0123
        r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-555-0123 or +1 555 0123
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (555) 123-4567
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 555-123-4567 or 555 123 4567
        r'\+\d{1,3}[-.\s]?\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-(555)-123-4567
    ]
    
    phones = []
    for pattern in phone_patterns:
        found_phones = re.findall(pattern, text)
        phones.extend(found_phones)
    
    if emails:
        entities['EMAIL'] = list(set(emails))
    if phones:
        entities['PHONE'] = list(set(phones))
    
    return entities

def parse_resume(file_path, file_extension):
    """Parse resume and return structured data"""
    text = extract_text(file_path, file_extension)
    if not text:
        return None
    
    entities = extract_entities(text)
    work_experiences = extract_work_experience(text)
    
    # Simple experience calculation (count years mentioned)
    experience_years = 0
    for date in entities['DATE']:
        if re.search(r'\d{4}', date):
            year = int(re.search(r'\d{4}', date).group())
            current_year = datetime.now().year
            if 1900 < year < current_year:
                experience_years = max(experience_years, current_year - year)
    
    # Prepare structured data
    data = {
        'full_name': entities['PERSON'][0] if entities['PERSON'] else "",
        'email': entities['EMAIL'][0] if entities['EMAIL'] else "",
        'phone': entities['PHONE'][0] if entities['PHONE'] else "",
        'location': entities['GPE'][0] if entities['GPE'] else "",
        'years_experience': min(experience_years, 30),  # Cap at 30 years
        'education': [],
        'skills': [{'name': skill, 'category': 'technical'} for skill in entities['ORG']],
        'work_experience': work_experiences
    }
    
    return data