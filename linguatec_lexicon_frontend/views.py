import logging
import urllib.parse
from collections import OrderedDict

import requests
from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import resolve, reverse
from django.views.generic.base import RedirectView, TemplateView

from linguatec_lexicon_frontend import utils
from linguatec_lexicon_frontend.forms import ConjugatorForm

logger = logging.getLogger(__name__)


# Helper to avoid repetitive boilerplate
def call_api(path, params=None, timeout=10):
    base_url = settings.LINGUATEC_LEXICON_API_URL.rstrip('/')
    url = f"{base_url}/{path.lstrip('/')}"
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        logger.exception(f"API request failed for {url}")
        return None
    except (ValueError, TypeError):
        # Catch json.JSONDecodeError (ValueError in Python < 3.5) and type errors
        logger.exception(f"Failed to decode JSON response from {url}")
        return None


def get_lexicons():
    data = call_api('lexicons/')
    if not data:
        return []
    lexicons = data.get("results", [])
    lexicons.sort(key=lambda x: x['name'])
    return lexicons


class MenuItem:
    """Define an item of the website menu."""
    def __init__(self, name, url, current_url=None):
        self.name = name
        self.url = url
        self.active = (self.url == current_url)


class LinguatecBaseView(TemplateView):
    """
    Base view that initializes the common context and
    the menu items of the website.
    """

    def get_context_data(self, **kwargs):
        current_view = resolve(self.request.path_info)
        context = super().get_context_data(**kwargs)

        context['menu'] = self.generate_menu_items(current_view.url_name)
        context['menu_footer_lg'] = self.generate_menu_footer_lg_items()

        # Modernized autocomplete URL
        base_url = settings.LINGUATEC_LEXICON_API_URL.rstrip('/')
        context['autocomplete_api_url'] = f"{base_url}/words/near/"

        context['fa_class'] = 'fal' if getattr(settings, 'LINGUATEC_FONTAWESOME_PRO', False) else 'fas'

        context['topic_list'] = [
            {
                "id": 17, "code": "es-ar", "name": "Botánico",
                "src_language": "es", "dst_language": "ar", "topic": "flora",
                "slug": "es-ar@flora", "icon": "fa-flower"
            },
            {
                "id": 18, "code": "es-ar", "name": "Faunístico",
                "src_language": "es", "dst_language": "ar", "topic": "fauna",
                "slug": "es-ar@fauna", "icon": "fa-paw"
            },
            {
                "id": 19, "code": "es-ar", "name": "Jurídico",
                "src_language": "es", "dst_language": "ar", "topic": "law",
                "slug": "es-ar@law", "icon": "fa-balance-scale"
            },
        ]
        return context

    def generate_menu_items(self, current_url_name):
        return (
            (
                MenuItem('Inicio', 'home', current_url_name),
                MenuItem('Proyecto Linguatec', 'linguatec-project', current_url_name),
                MenuItem('Contacto', 'contact', current_url_name),
                MenuItem('Ayuda', 'help', current_url_name),
            ),
            (
                MenuItem('Aviso legal', 'legal-notice', current_url_name),
                MenuItem('Política de privacidad', 'privacy-policy', current_url_name),
            ),
        )

    def generate_menu_footer_lg_items(self):
        return (
            MenuItem('Aviso legal', 'legal-notice'),
            MenuItem('Política de privacidad', 'privacy-policy'),
            MenuItem('Contacto', 'contact'),
            MenuItem('Ayuda', 'help'),
        )

    def groupby_word_entries(self, word):
        common = []
        variations = OrderedDict()
        for entry in word.get('entries', []):
            if entry.get('variation') is None:
                common.append(entry)
            else:
                region = entry['variation']['region']
                variations.setdefault(region, []).append(entry)

        word['entries_common'] = common
        word['entries_variations'] = variations

        ARAGONESE_LEXICON_CODE = 'ar-es'
        word['is_regular_verb'] = (word.get("lexicon") == ARAGONESE_LEXICON_CODE and utils.is_regular_verb(word))


class HomeView(LinguatecBaseView):
    template_name = 'linguatec_lexicon_frontend/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["first_load"] = self.request.session.get('first_load', True)
        self.request.session['first_load'] = False
        context['lexicons'] = get_lexicons()
        context['selected_lexicon'] = 'es-ar'
        return context


class HelpView(LinguatecBaseView):
    template_name = 'linguatec_lexicon_frontend/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gramcats"] = utils.retrieve_gramcats()
        return context


class ContactView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/contact.html"


class LegalNoticeView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/legal-notice.html"


class LinguatecProjectView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/linguatec-project.html"


class PrivacyPolicy(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/privacy-policy.html"


class SearchView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/search_results.html"

    def dispatch(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        query = request.GET.get('q')
        lex_slug = request.GET.get('l', '')

        if query:
            data = call_api('words/search/', params={'q': query, 'l': lex_slug})
            results = data.get("results", []) if data else []

            for word in results:
                self.groupby_word_entries(word)

            context.update({
                'query': query,
                'results': results,
                'selected_lexicon': lex_slug,
                'selected_lexicon_code': lex_slug.split("@")[0],
                'lexicons': get_lexicons(),
            })

            if not results:
                context["near_words"] = utils.retrieve_near_words(query, lex_slug)

        return TemplateResponse(request, self.template_name, context)


class WordDetailView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        word = self.get_word()
        term = urllib.parse.quote(word['term'], safe='')
        return reverse('word-detail-uri', args=(word['lexicon'], term))

    def get_word(self):
        pk = self.kwargs['pk']
        word = call_api(f'words/{pk}/')
        if not word:
            raise Http404("Word doesn't exist.")
        return word


class WordDetailBySlug(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        word = self.get_word()
        term = urllib.parse.quote(word['term'], safe='')
        return reverse('word-detail-uri', args=(word['lexicon'], term))

    def get_word(self):
        slug = self.kwargs['slug']
        word = call_api(f'words/slug/{slug}/')
        if not word:
            raise Http404("Word doesn't exist.")
        return word


class WordByURIDetailView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.lexicons = get_lexicons()
        word = self.get_word()
        self.groupby_word_entries(word)

        context.update({
            'results': [word],
            'selected_lexicon': word['lexicon'],
            'lexicons': self.lexicons,
        })
        return context

    def get_word(self):
        lexicon = self.clean_lexicon(self.kwargs['lexicon'])
        word_term = self.kwargs['word']
        word_data = call_api('words/exact/', params={'l': lexicon, 'q': word_term})
        if not word_data:
            raise Http404("Word doesn't exist.")
        return word_data

    def clean_lexicon(self, value):
        valid_slugs = [lex['slug'] for lex in self.lexicons]
        if value not in valid_slugs:
            raise Http404("Lexicon doesn't exist.")
        return value


class ConjugationDetailView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/word_entry_conjugation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "verb": kwargs.get('verb'),
            "lexicons": get_lexicons(),
            "selected_lexicon": 'es-ar',
            "conjugator_form": ConjugatorForm()
        })
        return context
