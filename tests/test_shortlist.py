import os
import unittest
from app.utils.parser import parse_resume
from app.utils.shortlister import rank_candidates

class TestShortlistingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Define test resume paths and expected job description"""
        cls.test_resume_dir = "test_resumes"
        cls.job_description = """
        We are looking for a Python developer with:
        - 3+ years experience with Flask/Django
        - Strong machine learning skills
        - Knowledge of cloud platforms (AWS preferred)
        - Experience with database systems
        """
        
        cls.expected_files = [
            "software_engineer.docx",
            "data_scientist.pdf",
            "cybersecurity_specialist.pdf"
        ]

    def test_resume_files_exist(self):
        """Verify test resume files are present"""
        for filename in self.expected_files:
            path = os.path.join(self.test_resume_dir, filename)
            self.assertTrue(os.path.exists(path), 
                          f"Test resume {filename} not found in {self.test_resume_dir}")

    def test_parse_and_shortlist(self):
        """Test complete parsing and shortlisting workflow"""
        candidates_data = []
        
        # 1. Parse all test resumes
        for filename in os.listdir(self.test_resume_dir):
            if filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                path = os.path.join(self.test_resume_dir, filename)
                try:
                    file_ext = os.path.splitext(filename)[1][1:].lower()
                    parsed = parse_resume(path, file_ext)
                    self.assertIsNotNone(parsed, f"Failed to parse {filename}")
                    
                    # Add candidate_id for database-like reference
                    parsed['candidate_id'] = len(candidates_data) + 1
                    candidates_data.append(parsed)
                    
                    # Basic validation of parsed data
                    self.assertTrue(parsed['full_name'], f"No name extracted from {filename}")
                    self.assertTrue(parsed['email'], f"No email extracted from {filename}")
                    self.assertTrue(parsed['skills'], f"No skills extracted from {filename}")
                    
                except Exception as e:
                    self.fail(f"Error processing {filename}: {str(e)}")

        # 2. Test shortlisting with realistic job description
        ranked_candidates = rank_candidates(self.job_description, candidates_data)
        
        # Basic validation of shortlisting results
        self.assertTrue(len(ranked_candidates) > 0, "No candidates were ranked")
        self.assertTrue(len(ranked_candidates) <= len(candidates_data), 
                       "Ranked more candidates than available")
        
        # Verify scores are within expected range
        for candidate in ranked_candidates:
            self.assertIsInstance(candidate['similarity_score'], float,
                                "Similarity score should be a float")
            self.assertTrue(0 <= candidate['similarity_score'] <= 1,
                          "Similarity score out of range (0-1)")
        
        # Print results for inspection
        print("\nShortlisting Results:")
        print(f"{'Rank':<5} | {'Score':<6} | {'Name':<20} | {'Top Skills'}")
        print("-" * 60)
        for i, candidate in enumerate(ranked_candidates, 1):
            top_skills = ', '.join([s['name'] for s in candidate['data']['skills'][:3]])
            print(f"{i:<5} | {candidate['similarity_score']:.4f} | {candidate['data']['full_name']:<20} | {top_skills}")

if __name__ == '__main__':
    unittest.main()