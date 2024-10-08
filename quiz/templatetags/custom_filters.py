from django import template

register = template.Library()

@register.filter
def to_char(index):
    return chr(index + 64)  # Chuyển đổi số thành ký tự A, B, C, D
