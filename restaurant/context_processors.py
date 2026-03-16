from .translations import TRANSLATIONS
from django.utils import translation

def language_context(request):
    lang = translation.get_language() or 'en'
    return {
        'lang_data': TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    }  

    