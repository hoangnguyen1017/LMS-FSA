from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course, Enrollment
from quiz.models import Quiz, StudentQuizAttempt
from user.models import User
from collections import Counter

# Create your views here.
def calculate(user_id, course_id):
    quizzes = Quiz.objects.filter(course=course_id).count()
    attempts = len(Counter(set(
        StudentQuizAttempt.objects.filter(user=user_id, quiz__course=course_id).values_list('quiz_id', flat=True)
        )))
    return quizzes, attempts

def progress_list(request):
    # print(request.user.name)
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    course = Enrollment.objects.filter(student=request.user)
    _dict = {"courses":None,
            "Percent":None}
    list = []
    for i in course:
        total, attempts = calculate(request.user, i.course.id)
        dict_ = dict(_dict)
        if total == 0:
            dict_['courses'] = i
            dict_['Percent'] = 0
        else:
            dict_['courses'] = i
            dict_['Percent'] = attempts / total * 100
        list.append(dict_)
    return render(request,'aggregated.html',{'module_groups': module_groups,
                                             'modules': modules,
                                             'courses': list,
                                             'course_count':len(list),
                                             'user': request.user })
