from django import template
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

PRONOUNS = {
    'he/she':   {'M': 'he',  'F': 'she'},
    'she/he':   {'M': 'he',  'F': 'she'},
    'him/her':  {'M': 'him', 'F': 'her'},
    'her/him':  {'M': 'him', 'F': 'her'},
    'his/her':  {'M': 'his', 'F': 'her'},
    'her/his':  {'M': 'his', 'F': 'her'},
    'his/hers': {'M': 'his', 'F': 'hers'},
    'hers/his': {'M': 'his', 'F': 'hers'},
}

@register.simple_tag
def scriptify(text, gender):
    for key, value in PRONOUNS.iteritems():
        text = text.replace(key, value.get(gender, key))
    return markdown.markdown(text)