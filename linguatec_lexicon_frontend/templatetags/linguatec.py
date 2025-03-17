"""
Templatetags helpers to render lexicon content.
"""
import re
import urllib.parse

import coreapi
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
    value = entry.get('marked_translation') or entry['translation']

    try:
        validators.validate_balanced_parenthesis(value)
    except ValidationError:
        # [readspeaker] wrap & identify entry to be read
        return "<span id='word_{}'>{}</span>".format(entry['id'], value)

    # [readspeaker] mark content in parenthesis & skip it to be read
    value = mark_safe(readspeaker_skip_variant_suffix(value))
    value = value.replace("(", "<span class='rg-usecase-comment rs_skip'>(")
    value = value.replace(")", ")</span>")

    # Replace <trans> mark with links to wrapped words
    value = re.sub(r'<trans word=([0-9]+)>(.*?)</trans>', build_link, value)

    # mark keywords (inline gramcat)
    value = highlight_gramcats_inline(value)

    # [readspeaker] wrap & identify entry to be read
    return "<span id='word_{}'>{}</span>".format(entry['id'], value)


def highlight_gramcats_inline(value):
    """
    Highlight inline gramcats abbreviations & add related title
    """
    gramcats = utils.retrieve_gramcats()
    gramcats.sort(key=sort_by_abbr_len, reverse=True)
    abbr_replaced = []
    for gramcat in gramcats:
        abbr, title = gramcat['abbreviation'], gramcat['title']

        # avoid double highlight for abbreviations that are a subset of another
        # e.g. 's.' is a subset of 's. m.'
        abbr_subset = False
        for replaced in abbr_replaced:
            if replaced.startswith(abbr):
                abbr_subset = True
                break

        if abbr_subset:
            continue

        # TODO(@slamora): are other expressions needed?
        expressions = [f"{abbr} ", f"({abbr})"]
        if any(expr in value for expr in expressions):
            abbr_replaced.append(abbr)
            value = value.replace(
                abbr, "<span class='rg-gramcat' title='{0}'>{1}</span>".format(title, abbr))

    return value


def sort_by_abbr_len(gramcat):
    return len(gramcat['abbreviation'])


def build_link(matchobj):
    return "<a class='{class}' href='/words/{id}/'>{word}</a>".format_map({
        'class': "rg-linked-word",
        'id': matchobj.group(1),
        'word': matchobj.group(2),
    })


@register.filter
@mark_safe
def render_term(word, lexicon_code):
    term = word['term']
    if lexicon_code == "ar-es":
        term = readspeaker_skip_variant_suffix(term)

    return '<span id="word_{}">{}</span>'.format(word['id'], term)


def readspeaker_skip_variant_suffix(term):
    # Match '/' excluding HTML closing tag: e.g. </span)
    return re.sub(r'(?<!<)([/]\w+)', '<span class="rs_skip">\g<0></span>', term)


# TODO unused???
@register.filter
@stringfilter
def verbose_gramcat(value):
    """Attach description to gramatical category abbreviature."""
    api_url = settings.LINGUATEC_LEXICON_API_URL
    client = coreapi.Client()
    schema = client.get(api_url)
    querystring_args = {'abbr': value}
    url = urllib.parse.urljoin(
        schema['gramcats'], 'show/?' + urllib.parse.urlencode(querystring_args))
    gramcat = client.get(url)

    return "{} ({})".format(gramcat['title'], gramcat['abbreviation'])
