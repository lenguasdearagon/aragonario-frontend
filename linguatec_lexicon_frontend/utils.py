"""
Utils to retrieve information of the lexicon backend API.
"""
import requests
from django.conf import settings


def is_regular_verb(word):
    ARAGONESE_VERB_SUFFIXES = ['ar', 'er', 'ir']
    GRAMCATS_REGULAR_VERBS = [
        "v.", "v. cop.", "v. intr.", "v. prnl.",
        "v. reciproc.", "v. tr.",
    ]
    PRONOMINOADVERBIALS = ['-bi', '-ie', '-ne']

    # 1. Check Grammatical Category
    if not any(cat in GRAMCATS_REGULAR_VERBS for cat in word.get("gramcats", [])):
        return False

    # 2. Detect conjugation potential
    word_root = word["term"]
    for pronominal in PRONOMINOADVERBIALS:
        # Using Python 3.9+ built-in removesuffix
        word_root = word_root.removesuffix(pronominal)

    # Check for -ar, -er, -ir or -se
    if any(word_root.endswith(s) for s in ARAGONESE_VERB_SUFFIXES):
        return True

    if word_root.endswith('-se'):
        return True

    return False


def retrieve_gramcats():
    """Retrieve all categories using standard REST calls."""
    # Ensure URL ends with a slash to avoid redirects
    base_url = settings.LINGUATEC_LEXICON_API_URL.rstrip('/')
    url = f"{base_url}/gramcats/"
    params = {'limit': 100}

    gramcats = []

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        gramcats.extend(data["results"])

        # 'next' will be a full URL provided by the DRF paginator
        url = data.get("next")
        params = None  # Parameters are already inside the 'next' URL

    return gramcats


def retrieve_near_words(query, lex):
    """Retrieve near words using standard REST calls."""
    base_url = settings.LINGUATEC_LEXICON_API_URL.rstrip('/')
    url = f"{base_url}/words/near/"
    params = {'q': query, 'l': lex}

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json().get("results", [])
