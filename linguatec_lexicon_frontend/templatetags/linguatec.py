"""
Templatetags helpers to render lexicon content.
"""
import re

import requests
from django import template
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from linguatec_lexicon_frontend import utils, validators

register = template.Library()

@register.filter
@mark_safe
def render_entry(entry):
    """Parse entry content to apply weight to content."""
    # Use modern .get() and fallback
    value = entry.get('marked_translation') or entry.get('translation', '')

    try:
        validators.validate_balanced_parenthesis(value)
    except ValidationError:
        return f"<span id='word_{entry['id']}'>{value}</span>"

    # [readspeaker] mark content in parenthesis & skip it to be read
    value = readspeaker_skip_variant_suffix(value)
    value = value.replace("(", "<span class='rg-usecase-comment rs_skip'>(")
    value = value.replace(")", ")</span>")

    # Replace <trans> mark with links using f-strings for Python 3.13 speed
    value = re.sub(r'<trans word=([0-9]+)>(.*?)</trans>', build_link, value)

    # mark keywords (inline gramcat)
    value = highlight_gramcats_inline(value)

    return f"<span id='word_{entry['id']}'>{value}</span>"


def highlight_gramcats_inline(value):
    """Highlight inline gramcats abbreviations & add related title."""
    # This calls utils.retrieve_gramcats() which now uses 'requests'
    gramcats = utils.retrieve_gramcats()

    # Sort by length descending to match longest abbreviations first
    # (e.g., 's. m.' before 's.')
    gramcats.sort(key=lambda x: len(x['abbreviation']), reverse=True)

    abbr_replaced = []
    for gramcat in gramcats:
        abbr, title = gramcat['abbreviation'], gramcat['title']

        # avoid double highlight for subsets
        if any(replaced.startswith(abbr) for replaced in abbr_replaced):
            continue

        # Check if abbreviation appears with/without parenthesis
        expressions = [rf"\b{re.escape(abbr)}", rf"\({re.escape(abbr)}\)"]
        if any(re.search(expr, value) for expr in expressions):
            abbr_replaced.append(abbr)
            # Use f-string for better performance in 3.13
            span = f"<span class='rg-gramcat' title='{title}'>{abbr}</span>"
            value = value.replace(abbr, span)

    return value


def build_link(matchobj):
    word_id = matchobj.group(1)
    word_text = matchobj.group(2)
    return f'<a class="rg-linked-word" href="/words/{word_id}/">{word_text}</a>'


@register.filter
@mark_safe
def render_term(word, lexicon_code):
    term = word.get('term', '')
    if lexicon_code == "ar-es":
        term = readspeaker_skip_variant_suffix(term)

    return f'<span id="word_{word["id"]}">{term}</span>'


def readspeaker_skip_variant_suffix(term):
    # Match '/' excluding HTML closing tag: e.g. </span>
    return re.sub(r'(?<!<)([/]\w+)', r'<span class="rs_skip">\1</span>', term)


@register.filter
@stringfilter
def verbose_gramcat(value):
    """Attach description to grammatical category abbreviation via Requests."""
    base_url = settings.LINGUATEC_LEXICON_API_URL.rstrip('/')
    url = f"{base_url}/gramcats/show/"

    try:
        response = requests.get(url, params={'abbr': value})
        response.raise_for_status()
        gramcat = response.json()
        return f"{gramcat['title']} ({gramcat['abbreviation']})"
    except (requests.RequestException, KeyError):
        return value        return value
