from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course, Enrollment
from quiz.models import Quiz, StudentQuizAttempt
from user.models import User
from collections import Counter
from django.core.paginator import Paginator
from .models import UserCourseProgress
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your views here.
def calculate(user_id, course_id):
    quizzes = Quiz.objects.filter(course=course_id).count()
    attempts = len(Counter(set(
        StudentQuizAttempt.objects.filter(user=user_id, quiz__course=course_id).values_list('quiz_id', flat=True)
        )))
    return quizzes, attempts

def progress_list(request):
    print(request.user)
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    course = Enrollment.objects.filter(student=request.user)
    _dict = {"courses":None,
            "Percent":None}
    _list = []
    for i in course:
        total, attempts = calculate(request.user, i.course.id)
        dict_ = dict(_dict)
        if total == 0:
            dict_['courses'] = i
            dict_['Percent'] = 0
        else:
            dict_['courses'] = i
            dict_['Percent'] = round(attempts / total * 100,2)
        if len(list(UserCourseProgress.objects.filter(user=request.user, course_id=dict_['courses'].course.id))) !=0:
            UserCourseProgress.objects.filter(user=request.user, course_id=dict_['courses'].course.id).update(
                progress_percentage=dict_['Percent']
            )
        else:
            UserCourseProgress.objects.create(
            user=request.user, 
            course=Course.objects.get(course_code=dict_['courses'].course.course_code), 
            progress_percentage=dict_['Percent']
        )
        _list.append(dict_)
    return render(request,'aggregated.html',{'module_groups': module_groups,
                                             'modules': modules,
                                             'courses': _list,
                                             'course_count':len(_list),
                                             'user': request.user })
