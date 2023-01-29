from django import template

register = template.Library()


@register.filter
def get_dict_item(dictionary, key):
    """Get Item of Dictionary"""
    return dictionary[key]


@register.simple_tag
def define(value=None):
    return value


@register.filter
def get_mm_ss_time(seconds):
    mins, secs = divmod(seconds, 60)
    if mins == 0:
        return str(secs) + 's'
    else:
        return str(mins) + 'm ' + str(secs) + 's'


@register.filter(name='split')
def split(str, key):
    return str.split(key)


@register.simple_tag
def bot_related_access_perm(user_obj, bot_pk):
    return user_obj.get_bot_related_access_perm(bot_pk)


@register.simple_tag
def bot_related_type_access(user_obj, bot_pk):
    return user_obj.get_bot_related_type_access(bot_pk)


@register.simple_tag
def overall_access_perm(user_obj, bot_pk):
    return user_obj.get_overall_access_perm(bot_pk)
