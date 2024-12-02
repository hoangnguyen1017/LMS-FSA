from django import template
from django.template.defaultfilters import date

register = template.Library()

@register.filter(name='get_author')
def get_author(thread, user):
    """Returns the author name based on anonymity and user permissions"""
    if user.is_staff or user.is_superuser:
        if thread.is_anonymous:
            return f"Anonymous (Actually: {thread.created_by.username})"
        return thread.created_by.username
    return "Anonymous" if thread.is_anonymous else thread.created_by.username

@register.filter
def get_display_name(thread):
    """
    Returns 'Anonymous' if the post is anonymous, otherwise returns the username
    """
    if thread.is_anonymous:
        return "Anonymous"
    return thread.created_by.username if thread.created_by else "Deleted User" 