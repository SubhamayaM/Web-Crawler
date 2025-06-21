from bs4 import NavigableString
from collections import Counter

def extract_and_score(soup, keywords):
    texts = soup.stripped_strings
    full_text = " ".join([str(t) for t in texts if isinstance(t, NavigableString)])
    lower_text = full_text.lower()

    # Count keyword frequency
    word_count = Counter(lower_text.split())
    match_score = sum(word_count[k] for k in keywords if k in word_count)

    return full_text, match_score
