from bs4 import NavigableString

def extract_and_filter(soup, keywords):
    texts = soup.stripped_strings
    full_text = " ".join([str(t) for t in texts if isinstance(t, NavigableString)])
    lower_text = full_text.lower()

    relevant = any(keyword in lower_text for keyword in keywords)
    return full_text, relevant
