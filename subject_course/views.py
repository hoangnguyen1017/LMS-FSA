# views.py
from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Material  # Import your Material model or the relevant model

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    return render(request, 'course/course_detail.html', {'course': course, 'lessons': lessons})

def lesson_detail(request, lesson_id):
    print(lesson_id)
    lesson = get_object_or_404(Lesson, id=lesson_id)
    materials = lesson.materials.all()
    return render(request, 'course/lesson_detail.html', {'lesson': lesson, 'materials': materials})
