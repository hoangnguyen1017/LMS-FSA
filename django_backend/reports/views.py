from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from course.models import Course, Enrollment, Session, Completion, Tag, CourseMaterial
from django.db.models import Count
from django.utils import timezone
from module_group.models import ModuleGroup

@login_required
def report_dashboard(request):
    module_groups = ModuleGroup.objects.all()
    return render(request, 'reports/dashboard_report.html', 
    {
        'module_groups': module_groups,
    })


@login_required
def course_overview_report(request):
    module_groups = ModuleGroup.objects.all()
    courses = Course.objects.all()
    return render(request, 'reports/course_overview_report.html', 
    {'courses': courses, 'module_groups': module_groups,
    })

@login_required
def student_enrollment_report(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    return render(request, 'reports/student_enrollment_report.html', {'enrollments': enrollments})

@login_required
def course_completion_report(request):
    user = request.user
    course_progress = {course: course.get_completion_percent(user) for course in Course.objects.all()}
    return render(request, 'reports/course_completion_report.html', {'course_progress': course_progress})

@login_required
def session_overview_report(request):
    sessions = Session.objects.select_related('course').all()
    return render(request, 'reports/session_overview_report.html', {'sessions': sessions})

@login_required
def material_usage_report(request):
    completions = Completion.objects.select_related('session', 'material', 'user').all()
    return render(request, 'reports/material_usage_report.html', {'completions': completions})

@login_required
def enrollment_trends_report(request):
    today = timezone.now()
    
    # Querying enrollments and annotating with count
    enrollments = (
        Enrollment.objects
        .filter(date_enrolled__month=today.month)
        .values('course__course_name')  # Get the course name by following the ForeignKey relationship
        .annotate(count=Count('id'))
    )

    return render(request, 'reports/enrollment_trends_report.html', {'enrollments': enrollments})
@login_required
def material_type_distribution_report(request):
    materials = CourseMaterial.objects.values('material_type').annotate(count=Count('id'))
    return render(request, 'reports/material_type_distribution_report.html', {'materials': materials})

@login_required
def tag_report(request):
    tags = Tag.objects.annotate(course_count=Count('courses'))
    return render(request, 'reports/tag_report.html', {'tags': tags})

@login_required
def user_progress_report(request):
    user = request.user
    progress = Completion.objects.filter(user=user).select_related('session', 'material')
    return render(request, 'reports/user_progress_report.html', {'progress': progress})

@login_required
def instructor_performance_report(request):
    instructors = Course.objects.values('instructor').annotate(enrollment_count=Count('enrollment')).order_by('-enrollment_count')
    return render(request, 'reports/instructor_performance_report.html', {'instructors': instructors})
