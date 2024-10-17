from django.shortcuts import render, redirect
from certificate.models import Certificate
from django.core.paginator import Paginator
from ai_insights.models import AIInsights
from performance_analytics.models import PerformanceAnalytics
from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course, Enrollment
from quiz.models import Quiz, StudentQuizAttempt
from user.models import User
from collections import Counter

def user_summary(request):
    return redirect('user_progress:user_progress_summary')


