# test_improved_resume.py
import sys
from pathlib import Path
import json

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent / "app" / "utils"))

# Import the improved parser
from parser import parse_resume

def test_resume_parsing():
    # Test with your sample PDF resume
    result = parse_resume("D:\Btech\Resume Processing System\Resumes\Resumes\Resume 2.docx", 'docx')
    
    if result:
        print("=== IMPROVED PARSING RESULTS ===\n")
        print(f"Full Name: {result['full_name']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")
        print(f"Location: {result['location']}")
        print(f"Years of Experience: {result['years_experience']}")
        
        print(f"\nEducation ({len(result['education'])} entries):")
        for edu in result['education']:
            print(f"  - {edu['degree']} | {edu['institution']} | {edu['year']}")
        
        print(f"\nSkills ({len(result['skills'])} entries):")
        skills_by_category = {}
        for skill in result['skills']:
            category = skill['category']
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill['name'])
        
        for category, skills in skills_by_category.items():
            print(f"  {category.title()}: {', '.join(skills)}")
        
        print(f"\nWork Experience ({len(result['work_experience'])} entries):")
        for exp in result['work_experience']:
            print(f"  - {exp['title']} | {exp['company']} | {exp['date_range']}")
            if exp['description']:
                print(f"    Description: {exp['description'][:100]}...")
        
        print("\n" + "="*50)
        print("JSON Output:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to parse resume")

if __name__ == "__main__":
    test_resume_parsing()