"""
Django URLs.
"""
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('aviso-legal/', views.LegalNoticeView.as_view(), name='legal-notice'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    path('ayuda/', views.HelpView.as_view(), name='help'),
    path('politica-de-privacidad/', views.PrivacyPolicy.as_view(), name='privacy-policy'),
    path('proyecto-linguatec/', views.LinguatecProjectView.as_view(), name='linguatec-project'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('words/<int:pk>/', views.WordDetailView.as_view(), name='word-detail'),
    path('words/slug/<str:slug>/', views.WordDetailBySlug.as_view(), name='word-detail-by-slug'),
    path('words/<str:verb>/conjugation/', views.ConjugationDetailView.as_view(), name='word-conjugation'),
     path('words/<str:lexicon>/<path:word>/', views.WordByURIDetailView.as_view(), name='word-detail-uri'),

    # redirect of external links
    path('external/lenguas-de-aragon/',
         RedirectView.as_view(url='http://lenguasdearagon.org'), name='lenguas-de-aragon'),
    path('external/traductor/',
         RedirectView.as_view(url='https://traduze.aragon.es'), name='traductor'),
    path('external/aragon-recursos-en-linea/',
         RedirectView.as_view(url='http://aragon.lenguasdearagon.org/'), name='aragon-recursos'),
    path('external/repositorio/',
         RedirectView.as_view(url='https://github.com/lenguasdearagon/'), name='repositorio')
]
