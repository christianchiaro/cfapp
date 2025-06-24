from django import template

register = template.Library()

@register.filter
def filter_by_stage(matches, stage):
    return [m for m in matches if m.stage == stage]

@register.filter
def exclude_stage(matches, stage):
    return [m for m in matches if m.stage != stage]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def group_list():
    return ['A', 'B']  # Ordine forzato