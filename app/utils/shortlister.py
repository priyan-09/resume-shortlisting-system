from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(job_description, candidate_data):
    """Calculate similarity between job description and candidate profile"""
    # Prepare candidate profile text
    candidate_text = f"""
    Candidate Profile:
    Name: {candidate_data['full_name']}
    Skills: {', '.join([skill['name'] for skill in candidate_data['skills']])}
    Experience: {candidate_data['years_experience']} years
    Education: {', '.join([edu['degree'] for edu in candidate_data['education']]) if candidate_data['education'] else 'Not specified'}
    """
    
    # Encode both texts
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    candidate_embedding = model.encode(candidate_text, convert_to_tensor=True)
    
    # Calculate cosine similarity
    similarity = util.pytorch_cos_sim(job_embedding, candidate_embedding).item()
    
    return similarity

def rank_candidates(job_description, candidates_data, top_percent=10):
    """Rank candidates based on similarity to job description and return top X%"""
    if not candidates_data:
        return []
    
    ranked = []
    
    for candidate in candidates_data:
        similarity = calculate_similarity(job_description, candidate)
        ranked.append({
            'candidate_id': candidate['candidate_id'],
            'similarity_score': similarity,
            'data': candidate
        })
    
    # Sort by similarity score (descending)
    ranked.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Calculate how many candidates make up the top percentage
    total_candidates = len(ranked)
    top_count = max(1, round(total_candidates * (top_percent / 100)))
    
    return ranked[:top_count]