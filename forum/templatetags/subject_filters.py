# forum/templatetags/subject_filters.py
from django import template
from subject.models import Subject

register = template.Library()

@register.filter
def get_selected_subject_name(subjects, selected_subject_id):
    selected_subject = subjects.filter(id=selected_subject_id).first()
    return selected_subject.name if selected_subject else ''
