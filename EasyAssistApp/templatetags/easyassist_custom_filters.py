from django import template
from EasyAssistApp.utils import get_masked_data_if_hashed

register = template.Library()


@register.filter
def mask_data(value):
    return get_masked_data_if_hashed(value)


@register.filter(name='subtract')
def subtract(number):
    return 4 - number
