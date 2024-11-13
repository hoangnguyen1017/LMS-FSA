from django.shortcuts import render, get_object_or_404
from course.models import Course, Enrollment, Session, Completion, Tag, CourseMaterial
from django.db.models import Count, F, Q
from module_group.models import ModuleGroup
from user.models import User, Student, Profile
from collections import Counter
from django.http import JsonResponse
from activity.models import UserActivityLog
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.shortcuts import render
import plotly.graph_objs as go
from django.utils.timezone import make_aware
from django.db.models.functions import ExtractQuarter, ExtractYear
from django.http import Http404
from collections import defaultdict
import calendar
import json


@login_required
def user_duration_login(request):
    user = request.user
    activity_logs = UserActivityLog.objects.filter(user=user).order_by('activity_timestamp')

    login_times = []
    logout_times = []

    # Lấy thời gian đăng nhập và đăng xuất
    for log in activity_logs:
        if log.activity_type == 'login':
            login_times.append(log.activity_timestamp)
        elif log.activity_type == 'logout':
            logout_times.append(log.activity_timestamp)

    # Tính toán thời gian phiên làm việc
    session_durations = []
    for login_time in login_times:
        # Tìm lần đăng xuất gần nhất sau thời gian đăng nhập
        logout_time = next((lt for lt in logout_times if lt > login_time), None)
        if logout_time:
            # Tính toán thời gian phiên
            duration = logout_time - login_time

            # Định dạng lại thời gian phiên thành chuỗi "X days, Y hours, Z minutes"
            days, seconds = duration.days, duration.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) % 60

            formatted_duration = f"{days} days, {hours} hours, {minutes} minutes"
            total_minutes = duration.total_seconds() // 60  # Tính tổng phút

            session_durations.append({
                'login_time': login_time,
                'logout_time': logout_time,
                'duration': formatted_duration,  # Lưu trữ dưới dạng chuỗi
                'total_minutes': total_minutes,  # Lưu trữ tổng phút
            })
    session_durations = session_durations[-10:]
    return render(request, 'reports/user/user_duration_login.html', {
        'session_durations': session_durations,
    })


@login_required
def login_frequency_report(request):
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    today = timezone.now()
    start_date = today - timedelta(days=30)

    if from_date:
        from_date_parsed = parse_date(from_date)
        if from_date_parsed:
            start_date = from_date_parsed

    if to_date:
        to_date_parsed = parse_date(to_date)
        if to_date_parsed:
            end_date = to_date_parsed
        else:
            end_date = today
    else:
        end_date = today

    # Tổng hợp dữ liệu đăng nhập theo ngày trong khoảng thời gian đã chọn
    login_data = (
        UserActivityLog.objects.filter(
            user=request.user,
            activity_type='login',
            activity_timestamp__range=[start_date, end_date]
        )
        .annotate(day=TruncDate('activity_timestamp'))
        .values('day')
        .annotate(login_count=Count('log_id'))
        .order_by('day')
    )

    times = [entry['day'].strftime('%Y-%m-%d') for entry in login_data]
    counts = [entry['login_count'] for entry in login_data]

    title = "Login frequency in the last 30 days"
    back_to_month = False

    return render(request, 'reports/user/login_frequency_report.html', {
        'times': times,
        'counts': counts,
        'title': title,
        'login_frequency': login_data,
        'from_date': from_date,
        'to_date': to_date,
        'back_to_month': back_to_month,
    })


@login_required
def user_statistics_report(request):
    module_groups = ModuleGroup.objects.all()
    today = timezone.localtime().date()
    start_of_month = today.replace(day=1)
    current_month = today.strftime("%B %Y")

    # Lấy tham số ngày đăng nhập từ URL nếu có
    login_date_str = request.GET.get('login_date')
    selected_users = []

    # Kiểm tra và chuyển đổi login_date_str thành ngày
    if login_date_str:
        try:
            login_date = datetime.strptime(login_date_str, '%Y-%m-%d').date()
            # Lọc người dùng đã đăng nhập vào ngày được chọn
            selected_users = UserActivityLog.objects.filter(
                activity_type='login',
                activity_timestamp__date=login_date,
                user__is_superuser=False
            ).values('user__username', 'user__email', 'user__date_joined').distinct()
        except ValueError:
            login_date = None  # Ngày không hợp lệ, bỏ qua

    # Tổng hợp số lần đăng nhập hàng ngày cho tháng hiện tại
    daily_login_counts = (
        UserActivityLog.objects.filter(
            activity_type='login',
            activity_timestamp__gte=start_of_month,
            activity_timestamp__lt=today + timezone.timedelta(days=1),
            user__is_superuser=False
        )
        .annotate(login_date=TruncDate('activity_timestamp'))
        .values('login_date')
        .annotate(user_count=Count('user', distinct=True))
        .order_by('login_date')
    )

    # Chuyển đổi dữ liệu cho biểu đồ
    login_dates = [entry['login_date'].strftime('%Y-%m-%d') for entry in daily_login_counts]
    user_counts = [entry['user_count'] for entry in daily_login_counts]

    # Truy vấn tất cả người dùng đăng nhập trong tháng hiện tại
    users = User.objects.filter(date_joined__gte=start_of_month, is_superuser=False)

    return render(request, 'reports/user/user_statistics_report.html',
                  {
                      'module_groups': module_groups,
                      'login_dates': login_dates,
                      'user_counts': user_counts,
                      'current_month': current_month,
                      'users': users,
                      'selected_users': selected_users,
                      'selected_date': login_date_str  # Truyền ngày đã chọn
                  })


def student_id_report(request):
    students = Student.objects.all()
    student_cohorts = {}
    total_students = 0  # Tổng số sinh viên

    for student in students:
        if student.student_code and student.student_code.startswith("SE"):
            cohort = student.student_code[2:4]
            student_cohorts.setdefault(cohort, []).append(student)

    labels = [f"SE{cohort}" for cohort in student_cohorts.keys()]  # Thêm 'SE' vào nhãn
    data = [len(students) for students in student_cohorts.values()]
    total_students = sum(data)

    # Tạo bảng tổng kết
    cohort_summary = [
        {
            'label': label,
            'count': count,
            'percentage': (count / total_students) * 100 if total_students > 0 else 0
        }
        for label, count in zip(labels, data)
    ]

    context = {
        'labels': labels,
        'data': data,
        'cohort_summary': cohort_summary,
    }

    return render(request, 'reports/user/student_id_report.html', context)


def get_students_by_cohort(request, cohort):
    """Lấy danh sách sinh viên theo cohort cho yêu cầu AJAX"""
    students = Student.objects.filter(student_code__startswith=f"SE{cohort}")
    student_data = [{"name": student.user.username, "student_code": student.student_code} for student in students]
    return JsonResponse(student_data, safe=False)


def role_report(request):
    # Lấy số lượng người dùng theo vai trò
    role_counts = Profile.objects.values('role__role_name').annotate(user_count=Count('user')).order_by(
        'role__role_name')

    context = {
        'role_counts': role_counts,
    }

    return render(request, 'reports/user/role_report.html', context)


@login_required
def user_overview_report(request):
    # Lấy tất cả người dùng (trừ superusers)
    users = User.objects.exclude(is_superuser=True)

    return render(request, 'reports/user/user_overview_report.html', {'users': users})


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


def get_quarter(month):
    if 1 <= month <= 3:
        return 1
    elif 4 <= month <= 6:
        return 2
    elif 7 <= month <= 9:
        return 3
    else:
        return 4


@login_required
def enrollment_trends_report(request):
    all_courses = Course.objects.all()

    # Get current year and month if not specified
    current_date = timezone.now()
    year = int(request.GET.get('year', current_date.year))
    month = request.GET.get('month')  # Optional month filter

    # Get course_id from request, default to first course if none selected
    course_id = request.GET.get('course_id')
    if not course_id and all_courses.exists():
        course_id = all_courses.first().id
    elif not all_courses.exists():
        raise Http404("No courses available.")

    course = get_object_or_404(Course, pk=course_id)

    # Initialize data dictionaries
    enrollment_data = {month: 0 for month in range(1, 13)}
    unenrollment_data = {month: 0 for month in range(1, 13)}
    weekly_enrollment_data = defaultdict(int)
    weekly_unenrollment_data = defaultdict(int)

    # Base query for enrollments
    enrollments_query = Enrollment.objects.filter(
        course_id=course_id,
        date_enrolled__year=year,
        is_active=True
    )

    unenrollments_query = Enrollment.objects.filter(
        course_id=course_id,
        date_enrolled__year=year,
        is_active=False
    )

    if month:
        # If month is selected, show weekly data for that month
        month = int(month)
        enrollments_query = enrollments_query.filter(date_enrolled__month=month)
        unenrollments_query = unenrollments_query.filter(date_enrolled__month=month)

        # Group by week
        for enrollment in enrollments_query:
            week_number = enrollment.date_enrolled.isocalendar()[1]
            weekly_enrollment_data[week_number] += 1

        for unenrollment in unenrollments_query:
            week_number = unenrollment.date_enrolled.isocalendar()[1]
            weekly_unenrollment_data[week_number] += 1

        # Get all weeks in the selected month
        _, num_days = calendar.monthrange(year, month)
        start_date = make_aware(datetime(year, month, 1))
        end_date = make_aware(datetime(year, month, num_days))

        # Generate week labels
        week_labels = []
        current_date = start_date
        while current_date <= end_date:
            week_num = current_date.isocalendar()[1]
            if f"Week {week_num}" not in week_labels:
                week_labels.append(f"Week {week_num}")
            current_date += timedelta(days=1)

        chart_labels = week_labels
        chart_enrollment_data = [weekly_enrollment_data.get(week, 0) for week in range(1, len(week_labels) + 1)]
        chart_unenrollment_data = [weekly_unenrollment_data.get(week, 0) for week in range(1, len(week_labels) + 1)]
    else:
        # Show monthly data
        for enrollment in enrollments_query:
            enrollment_data[enrollment.date_enrolled.month] += 1

        for unenrollment in unenrollments_query:
            unenrollment_data[unenrollment.date_enrolled.month] += 1

        chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        chart_enrollment_data = list(enrollment_data.values())
        chart_unenrollment_data = list(unenrollment_data.values())

    context = {
        'course': course,
        'course_id': int(course_id),
        'year': year,
        'selected_month': month,
        'enrollment_data': enrollment_data,
        'unenrollment_data': unenrollment_data,
        'all_courses': all_courses,
        'chart_labels': json.dumps(chart_labels),  # Convert to JSON
        'chart_enrollment_data': json.dumps(chart_enrollment_data),  # Convert to JSON
        'chart_unenrollment_data': json.dumps(chart_unenrollment_data),  # Convert to JSON
        'months': [
            {'number': i, 'name': calendar.month_name[i]}
            for i in range(1, 13)
        ],
        # Add data for table
        'table_data': zip(chart_labels, chart_enrollment_data, chart_unenrollment_data)
    }

    return render(request, 'reports/enrollment_trends_report.html', context)


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
    instructors = Course.objects.values('instructor__username', 'course_name').annotate(
        enrollment_count=Count('enrollments')
    ).order_by('instructor__username', '-enrollment_count')

    return render(request, 'reports/instructor_performance_report.html', {'instructors': instructors})
