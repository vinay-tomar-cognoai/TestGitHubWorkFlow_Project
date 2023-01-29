import random
from django import template

register = template.Library()


@register.simple_tag
def random_int(number_one, number_two):
    return round(random.uniform(number_one, number_two), 2)


@register.simple_tag
def get_utils_data(input_string, index):
    required_data = ""
    try:
        required_data = input_string.split("$$$")[index]
    except Exception:
        pass

    return required_data


@register.simple_tag
def tell_number_type(number):
    try:
        number = int(number)
        if number > 0:
            return "positive"
        elif number < 0:
            return "negative"
        else:
            return "zero"
    except Exception:
        return "no data"


@register.simple_tag
def check_if_supervisor_has_agents_bot(agent, supervisor):
    try:
        return agent.check_supervisor_bot(supervisor)
    except Exception:
        return False


@register.simple_tag
def is_numeric(value):
    try:
        return isinstance(value, (int, str))
    except Exception:
        return False    
