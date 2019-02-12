# linguatec lexicon frontend
Frontend website based on vue.js

## Development
``TODO``

node.js and npm
```
sudo apt-get install --no-install-recommends nodejs npm
```

### Run tests
The tests included are build using Python [unittest](https://docs.python.org/3/library/unittest.html) library.
To run it just execute:
```bash
python -m unittest -v linguatec_lexicon_frontend.tests
```

## Deployment

```
django-admin startproject frontend

```

Update settings to include app as installed and set URL of the linguatec lexicon API:
```
# settings.py
INSTALLED_APPS = [
    ...
    'linguatec_lexicon_frontend',
]

STATIC_ROOT = '/home/linguatec/frontend/static/'

# Linguatec lexicon backend API URL
LINGUATEC_LEXICON_API_URL = 'https://api.example.org/'

```

Update `urls.py`
```
# urls.py
urlpatterns = [
    ...
    path('', include('linguatec_lexicon_frontend.urls')),
]
```
