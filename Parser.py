from bs4 import NavigableString

def extract_and_score(soup, keywords):
    texts = soup.stripped_strings
    full_text = " ".join([str(t) for t in texts if isinstance(t, NavigableString)])
    lower_text = full_text.lower()

    matched_keywords = [kw for kw in keywords if kw in lower_text]
    score = len(matched_keywords)

    return full_text, score, matched_keywords

