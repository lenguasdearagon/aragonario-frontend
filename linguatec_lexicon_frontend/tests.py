"""
Unit tests.
"""

import unittest
from unittest import mock

from linguatec_lexicon_frontend.templatetags import linguatec
from linguatec_lexicon_frontend.utils import is_regular_verb


class RenderEntryTestCase(unittest.TestCase):
    @mock.patch('linguatec_lexicon_frontend.utils.retrieve_gramcats')
    def test_render(self, retrieve_gramcats):
        retrieve_gramcats.return_value = []
        entry = {}
        entry['id'] = 1
        entry['translation'] = "boira (lorem ipsum)"
        entry['marked_translation'] = "<trans word=2>boira</trans> (lorem ipsum)"
        html = linguatec.render_entry(entry)
        self.assertIn("<span class='rg-usecase-comment rs_skip'>(lorem ipsum)</span>", html)
        self.assertIn(
            "<span id='word_1'><a class='rg-linked-word' href='/words/2/'>boira</a>", html)

    @mock.patch('linguatec_lexicon_frontend.utils.retrieve_gramcats')
    def test_render_begin(self, retrieve_gramcats):
        retrieve_gramcats.return_value = []
        entry = {}
        entry['id'] = 1
        entry['translation'] = "(foo) boira grasa"
        entry['marked_translation'] = "(foo) <trans word=2>boira</trans> <trans word=3>grasa</trans>"
        html = linguatec.render_entry(entry)
        self.assertIn("<span class='rg-usecase-comment rs_skip'>(foo)</span>", html)
        self.assertIn(
            "<a class='rg-linked-word' href='/words/2/'>boira</a> "
            "<a class='rg-linked-word' href='/words/3/'>grasa</a>",
            html
        )

    def test_render_unbalanced_parenthesis(self):
        entry = {}
        entry['id'] = 1
        entry['translation'] = "(foo)) invalid"
        entry['marked_translation'] = None
        html = linguatec.render_entry(entry)
        self.assertEqual("<span id='word_1'>(foo)) invalid</span>", html)


class RenderTermTest(unittest.TestCase):
    def test_basecase_not_aragonese(self):
        word = {
            "id": 1,
            "term": "casa",
        }
        output = linguatec.render_term(word, "es-ar")
        self.assertEqual('<span id="word_1">casa</span>', output)

    def test_basecase(self):
        word = {
            "id": 2,
            "term": "boira",
        }
        output = linguatec.render_term(word, "ar-es")
        self.assertEqual('<span id="word_2">boira</span>', output)

    def test_term_with_gender_variant(self):
        word = {
            "id": 3,
            "term": "ornicau/ada",
        }
        output = linguatec.render_term(word, "ar-es")
        self.assertEqual('<span id="word_3">ornicau<span class="rs_skip">/ada</span></span>', output)

    def test_term_with_gender_variant_multi_items(self):
        word = {
            "id": 3,
            "term": "escusón/ona, forrón/ona",
        }
        output = linguatec.render_term(word, "ar-es")
        self.assertEqual(
            '<span id="word_3">'
            'escusón<span class="rs_skip">/ona</span>, '
            'forrón<span class="rs_skip">/ona</span>'
            '</span>', output)


class SkipVariantSuffixTest(unittest.TestCase):
    def test_htaml(self):
        value = "<span>escusón/ona</span>"
        output = linguatec.readspeaker_skip_variant_suffix(value)
        self.assertEqual(
            '<span>escusón'
            '<span class="rs_skip">/ona</span>'
            '</span>', output)


class IsRegularVerbTestCase(unittest.TestCase):
    def test_suffix_ar(self):
        word = {
            "gramcats": ["v."],
            "term": "chugar",
        }
        self.assertTrue(is_regular_verb(word))

    def test_suffix_pronominoadv(self):
        word = {
            "gramcats": ["v. prnl."],
            "term": "fer-se-ne",
        }
        self.assertTrue(is_regular_verb(word))

    def test_not_verb(self):
        word = {
            "gramcats": ["s."],
            "term": "mercader",
        }
        self.assertFalse(is_regular_verb(word))


@mock.patch(
    'linguatec_lexicon_frontend.utils.retrieve_gramcats',
    return_value=[
        {"abbreviation": "s.", "title": "sustantivo"},
        {"abbreviation": "s. f.", "title": "sustantivo femenino"},
        {"abbreviation": "s. m.", "title": "sustantivo masculino"},
        {"abbreviation": "v. tr.", "title": "verbo transitivo"},
        {"abbreviation": "v. intr.", "title": "verbo intransitivo"},
    ]
)
class HightlightInlineGramCats(unittest.TestCase):
    def test_one(self, retrieve_gramcats):
        # es-ar: desfiladero --> gáriz (s. f. )
        input = "gáriz (s. f. )"
        expected = "gáriz (<span class='rg-gramcat' title='sustantivo femenino'>s. f.</span> )"

        output = linguatec.highlight_gramcats_inline(input)
        self.assertEqual(expected, output)

    def test_two(self, retrieve_gramcats):
        # an-an: au
        input = "... tiene amnios y alantoides."
        expected = "... tiene amnios y alantoides."

        output = linguatec.highlight_gramcats_inline(input)
        self.assertEqual(expected, output)

    def test_three(self, retrieve_gramcats):
        # es-ar: destacar |	v. tr. // v. intr. | (resaltar, poner de relieve) acobaltar // v. intr. (sobresalir, decollar) sobrexir, estar siñalero/a // v. tr. (adelantar una porción de tropa, separándola del cuerpo principal) abanzar (del lat. vulgar abantiare)
        input = "v. intr. (sobresalir, decollar) sobrexir, estar siñalero/a"
        expected = "<span class='rg-gramcat' title='verbo intransitivo'>v. intr.</span> (sobresalir, decollar) sobrexir, estar siñalero/a"

        output = linguatec.highlight_gramcats_inline(input)
        self.assertEqual(expected, output)

    def test_four(self, retrieve_gramcats):
        # es-ar: bandurria común
        input = "iba cuelliblanca (s. f.), ibis cuelliblanco (s. m.)"
        expected = "iba cuelliblanca (<span class='rg-gramcat' title='sustantivo femenino'>s. f.</span>), ibis cuelliblanco (<span class='rg-gramcat' title='sustantivo masculino'>s. m.</span>)"

        output = linguatec.highlight_gramcats_inline(input)
        self.assertEqual(expected, output)

    def test_five(self, retrieve_gramcats):
        # an-an: plorar
        input = "Redamar glarimas. Manar d'os uellos un liquido."
        expected = "Redamar glarimas. Manar d'os uellos un liquido."

        output = linguatec.highlight_gramcats_inline(input)
        self.assertEqual(expected, output)
