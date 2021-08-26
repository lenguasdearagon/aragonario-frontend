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
        entry['marked_translation'] = "<trans lex=ar-es>boira</trans> (lorem ipsum)"
        html = linguatec.render_entry(entry)
        self.assertIn("<span class='rg-usecase-comment'>(lorem ipsum)</span>", html)
        self.assertIn(
            "<span id='word_1'><a class='rg-linked-word' href='/search/?q=boira&l=ar-es'>boira</a> </span>", html)

    @mock.patch('linguatec_lexicon_frontend.utils.retrieve_gramcats')
    def test_render_begin(self, retrieve_gramcats):
        retrieve_gramcats.return_value = []
        entry = {}
        entry['id'] = 1
        entry['translation'] = "(foo) boira grasa"
        entry['marked_translation'] = "(foo) <trans lex=ar-es>boira</trans> <trans lex=ar-es>grasa</trans>"
        html = linguatec.render_entry(entry)
        self.assertIn("<span class='rg-usecase-comment'>(foo)</span>", html)
        self.assertIn(
            "<span id='word_1'> <a class='rg-linked-word' href='/search/?q=boira&l=ar-es'>boira</a> "
            "<a class='rg-linked-word' href='/search/?q=grasa&l=ar-es'>grasa</a></span>",
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
