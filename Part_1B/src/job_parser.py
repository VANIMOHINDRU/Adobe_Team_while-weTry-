def parse_job(path):
    with open(path, 'r', encoding='utf-8') as f:
        job_text = f.read().strip()

    keywords = extract_keywords(job_text)

    return {
        "description": job_text,
        "keywords": keywords
    }

def extract_keywords(text):
    # Simple keyword extraction — can improve with NLP later
    import re
    words = re.findall(r'\b\w+\b', text.lower())
    common_terms = {"and", "the", "on", "for", "with", "to", "a", "of", "in"}
    return sorted(list(set([w for w in words if len(w) > 3 and w not in common_terms])))
