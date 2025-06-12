from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    print(f"[TEMPLATE_FILTER] get_item: key={key}, value={dictionary.get(key)}")
    return dictionary.get(key)

@register.filter
def lookup(dictionary, key):
    print(f"[TEMPLATE_FILTER] lookup: key={key}, value={dictionary.get(str(key))}")
    return dictionary.get(str(key), '')