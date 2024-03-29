"""
The views.
"""
import urllib.parse
from collections import OrderedDict

import coreapi
from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import resolve, reverse
from django.views.generic.base import RedirectView, TemplateView

from linguatec_lexicon_frontend import utils
from linguatec_lexicon_frontend.forms import ConjugatorForm


def get_lexicons():
    client = coreapi.Client()
    schema = client.get(settings.LINGUATEC_LEXICON_API_URL)

    url = schema['lexicons']
    response = client.get(url)
    lexicons = response["results"]

    lexicons.sort(key=lambda x: x['name'])

    return lexicons


class MenuItem(object):
    """Define a item of the website menu."""
    name = ''
    url = ''
    active = False

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
        # detect active menu-item
        current_view = resolve(self.request.path_info)

        context = super().get_context_data(**kwargs)
        context['menu'] = self.generate_menu_items(current_view.url_name)
        context['menu_footer_lg'] = self.generate_menu_footer_lg_items()

        api_url = settings.LINGUATEC_LEXICON_API_URL
        client = coreapi.Client()
        schema = client.get(api_url)
        context['autocomplete_api_url'] = schema['words'] + 'near/'

        # Font Awesome Free or PRO
        if getattr(settings, 'LINGUATEC_FONTAWESOME_PRO', False):
            context['fa_class'] = 'fal'
        else:
            context['fa_class'] = 'fas'

        # TODO(@slamora): replace hardcoded list
        context['topic_list'] = [
            {
                "id": 17,
                "code": "es-ar",
                "name": "Botánico",
                "src_language": "es",
                "dst_language": "ar",
                "topic": "flora",
                "slug": "es-ar@flora",
                "icon": "fa-flower",
            },
            {
                "id": 18,
                "code": "es-ar",
                "name": "Faunístico",
                "src_language": "es",
                "dst_language": "ar",
                "topic": "fauna",
                "slug": "es-ar@fauna",
                "icon": "fa-paw",
            },
            {
                "id": 19,
                "code": "es-ar",
                "name": "Jurídico",
                "src_language": "es",
                "dst_language": "ar",
                "topic": "law",
                "slug": "es-ar@law",
                "icon": "fa-balance-scale",
            }
        ]

        return context

    def generate_menu_items(self, current_url_name):
        """Generate main menu navbar items."""
        urls = (
            (
                MenuItem('Inicio', 'home', current_url_name),
                MenuItem('Proyecto Linguatec',
                         'linguatec-project', current_url_name),
                MenuItem('Contacto', 'contact', current_url_name),
                MenuItem('Ayuda', 'help', current_url_name),
            ),
            (
                MenuItem('Aviso legal', 'legal-notice', current_url_name),
                MenuItem('Política de privacidad',
                         'privacy-policy', current_url_name),
            ),
        )

        return urls  # menu

    def generate_menu_footer_lg_items(self):
        """Generate footer menu used on lg+ devices."""
        urls = (
            MenuItem('Aviso legal', 'legal-notice'),
            MenuItem('Política de privacidad', 'privacy-policy'),
            MenuItem('Contacto', 'contact'),
            MenuItem('Ayuda', 'help'),
        )
        return urls

    def groupby_word_entries(self, word):
        """Group entries by variation.region"""
        common = []
        variations = OrderedDict()
        for entry in word['entries']:
            if entry['variation'] is None:
                common.append(entry)
            else:
                region = entry['variation']['region']
                if region not in variations:
                    variations[region] = []
                # TODO if we want to include gramcats may be inline
                # entry['gramcats_inline'] = ' / '.join([x['abbreviation'] for x in entry['gramcats']])
                variations[region].append(entry)
        word['entries_common'] = common
        word['entries_variations'] = variations

        # check if word is a verb to generate conjugator link
        ARAGONESE_LEXICON_CODE = 'ar-es'
        if word["lexicon"] == ARAGONESE_LEXICON_CODE:
            word['is_regular_verb'] = utils.is_regular_verb(word)
        else:
            # avoid trying to conjugate not Aragonese words
            word['is_regular_verb'] = False


class HomeView(LinguatecBaseView):
    template_name = 'linguatec_lexicon_frontend/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # show or not splash screen
        context["first_load"] = self.request.session.get('first_load', True)
        self.request.session['first_load'] = False

        context['lexicons'] = get_lexicons()
        # keep UI behaviour: set default lexicon 'es-ar'
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
        """Search and show results. If none, show near words."""
        context = self.get_context_data(**kwargs)
        query = request.GET.get('q', None)
        lex_slug = request.GET.get('l', '')
        if query is not None:
            client = coreapi.Client()
            schema = client.get(settings.LINGUATEC_LEXICON_API_URL)

            querystring_args = {'q': query, 'l': lex_slug}
            url = schema['words'] + 'search/?' + \
                urllib.parse.urlencode(querystring_args)
            response = client.get(url)
            results = response["results"]

            for word in results:
                self.groupby_word_entries(word)

            context.update({
                'query': query,
                'results': results,
                'selected_lexicon': lex_slug,
                'selected_lexicon_code': lex_slug.split("@")[0],
                'lexicons': get_lexicons(),
            })

            if response["count"] == 0:
                context["near_words"] = utils.retrieve_near_words(query, lex_slug)

        return TemplateResponse(request, 'linguatec_lexicon_frontend/search_results.html', context)


class WordDetailView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        word = self.get_word()
        term = urllib.parse.quote_plus(word['term'])
        return reverse('word-detail-uri', args=(word['lexicon'], term))

    def get_word(self):
        api_url = settings.LINGUATEC_LEXICON_API_URL
        client = coreapi.Client()
        schema = client.get(api_url)

        pk = self.kwargs['pk']
        url = schema['words'] + '{pk}/'.format(pk=pk)

        try:
            word = client.get(url)
        except coreapi.exceptions.ErrorMessage:
            raise Http404("Word doesn't exist.")

        return word


class WordDetailBySlug(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        word = self.get_word()
        term = urllib.parse.quote_plus(word['term'])
        return reverse('word-detail-uri', args=(word['lexicon'], term))

    def get_word(self):
        api_url = settings.LINGUATEC_LEXICON_API_URL
        client = coreapi.Client()
        schema = client.get(api_url)

        slug = self.kwargs['slug']
        url = schema['words'] + 'slug/{slug}/'.format(slug=slug)

        try:
            word = client.get(url)
        except coreapi.exceptions.ErrorMessage:
            raise Http404("Word doesn't exist.")

        return word


class WordByURIDetailView(LinguatecBaseView):
    """Display a word."""
    template_name = "linguatec_lexicon_frontend/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.lexicons = get_lexicons()

        word = self.get_word()
        self.groupby_word_entries(word)
        selected_lexicon = word['lexicon']

        context.update({
            'results': [word],
            'selected_lexicon': selected_lexicon,
            'lexicons': self.lexicons,
        })

        return context

    def get_word(self):
        lexicon = self.clean_lexicon(self.kwargs['lexicon'])
        word = self.kwargs['word']

        api_url = settings.LINGUATEC_LEXICON_API_URL
        client = coreapi.Client()
        schema = client.get(api_url)

        url = f"{schema['words']}exact/?l={lexicon}&q={word}"
        try:
            word = client.get(url)
        except coreapi.exceptions.ErrorMessage:
            raise Http404("Word doesn't exist.")

        return word

    def clean_lexicon(self, value):
        valid_slugs = [lexicon['slug'] for lexicon in self.lexicons]
        if value not in valid_slugs:
            raise Http404("Lexicon doesn't exist.")
        return value


class ConjugationDetailView(LinguatecBaseView):
    template_name = "linguatec_lexicon_frontend/word_entry_conjugation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verb = kwargs.get('verb')
        conjugator_form = ConjugatorForm()

        context.update({
            "verb": verb,
            "lexicons": get_lexicons(),
            "selected_lexicon": 'es-ar',  # keep UI behaviour: set default lexicon 'es-ar'
            "conjugator_form": conjugator_form
        })

        return context
