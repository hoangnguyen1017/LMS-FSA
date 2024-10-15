# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import UserActivityLog

# @login_required
# def activity_view(request):
#     # Log page visit for activity view
#     UserActivityLog.objects.create(user=request.user, activity_type='page_visit', activity_details='Visited activity page.')

#     # Logic to display user activity
#     activity_logs = UserActivityLog.objects.filter(user=request.user).order_by('-activity_timestamp')
#     context = {'activity_logs': activity_logs}
#     return render(request, 'activity.html', context)

from django.shortcuts import render
from django.core.paginator import Paginator 
from .models import UserActivityLog

def activity_view(request):
    # Log page visit for activity view
    UserActivityLog.objects.create(user=request.user, activity_type='page_visit', activity_details='Visited activity page.')

    # Logic to display user activity
    activity_logs = UserActivityLog.objects.filter(user=request.user).order_by('-activity_timestamp')
    paginator = Paginator(activity_logs, 40)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'activity.html', context)
