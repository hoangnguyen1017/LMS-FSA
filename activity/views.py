from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserActivityLog
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

@login_required
def activity_view(request):
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    # Get all activity logs and order them by newest first
    activity_logs = UserActivityLog.objects.all().order_by('-activity_timestamp')

    # Filter by search query
    if search_query:
        activity_logs = activity_logs.filter(activity_details__icontains=search_query)

    # Filter by date range
    if from_date:
        from_date_parsed = parse_date(from_date)
        if from_date_parsed:
            activity_logs = activity_logs.filter(activity_timestamp__gte=from_date_parsed)

    if to_date:
        to_date_parsed = parse_date(to_date)
        if to_date_parsed:
            # Add 1 day to include the entire to_date
            to_date_with_time = datetime.combine(to_date_parsed, datetime.max.time())
            activity_logs = activity_logs.filter(activity_timestamp__lte=to_date_with_time)

    page_number = request.GET.get('page', 1)
    page_size = 20
    paginator = Paginator(activity_logs, page_size)
    activity_logs_page = paginator.get_page(page_number)

    # Calculate the page range
    page_range_start = max(activity_logs_page.number - 2, 1)
    page_range_end = min(activity_logs_page.number + 2, paginator.num_pages)
    page_range = range(page_range_start, page_range_end + 1)  # Include end page

    # Calculate the start index for the current page
    activity_logs_page.start_index = (activity_logs_page.number - 1) * page_size + 1

    return render(request, 'activity.html', {
        'activity_logs': activity_logs_page,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
        'page_range': page_range,  # Pass page range to template
    })
