#add this into Middleware in settings.py (Ex:MIDDLEWARE = [
#    'django.middleware.security.SecurityMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#   'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'activity.activity_tracking_middleware.ActivityTrackingMiddleware',        add like this 
#])

from django.utils import timezone
from django.urls import resolve
from .models import UserActivityLog

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Log activity if the user is authenticated
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='page_visit',  # Use an appropriate activity type
                activity_details=f"Accessed {current_url}",
                activity_timestamp=timezone.now()  # This can be omitted since `auto_now_add` is used
            )

        return response