from django.shortcuts import render
from .models import PerformanceAnalytics
from user.models import User
# Create your views here.

def performance_analytics_view(request):
    analytics_data = PerformanceAnalytics.objects.all()
    print(analytics_data)
    return render(request, 'base.html', {'analytics_data': analytics_data})
def home_view(request):
    return render(request, 'home.html',{})

def base_view(request):
    return render(request, 'base.html',{})

