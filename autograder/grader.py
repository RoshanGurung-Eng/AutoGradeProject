# autograder/grader.py
"""Grading functions with robust tokenization"""

import re

def grade_text(student_text, expected_keywords=None):
    """
    Grade raw student answer text against expected keywords.
    Uses robust tokenization to handle punctuation/quotes.
    Returns: (score: float, matched: set, missing: set)
    """
    from .config import EXPECTED_KEYWORDS
    
    # Get keywords (from DB or config fallback)
    if expected_keywords is None:
        keywords = set(EXPECTED_KEYWORDS)
    else:
        keywords = set(kw.strip().lower() for kw in expected_keywords if kw.strip())
    
    if not keywords or not student_text.strip():
        return 0.0, set(), set(keywords) if keywords else set()
    
    # 🔥 ROBUST TOKENIZATION: Extract ONLY alphabetic sequences (ignore punctuation/quotes/brackets)
    student_words = set(
        word.lower() 
        for word in re.findall(r'[a-zA-Z]{2,}', student_text)  # Min 2 letters to avoid noise
    )
    
    # Match keywords
    matched = student_words & keywords
    missing = keywords - matched
    score = len(matched) / len(keywords) if keywords else 0.0
    
    # Debug info (optional - remove in production)
    print(f"\n🔍 Student tokens (first 20): {list(student_words)[:20]}")
    print(f"🔍 Matched: {sorted(matched)}")
    print(f"🔍 Missing: {sorted(missing)}")
    
    return score, matched, missing