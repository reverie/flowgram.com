from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

register = template.Library()

@stringfilter
def chop_at(value, string):
    indexOfString = value.find(force_unicode(string))
    if indexOfString >= 0:
        return value[0:indexOfString]
    return value

register.filter('chop_at', chop_at)


@stringfilter
def truncate(value, max_chars):
    if len(value) > max_chars:
        return value[0:max_chars - 3] + "..."
    else:
        return value

register.filter('truncate', truncate)
