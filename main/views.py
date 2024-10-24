from django.shortcuts import render, redirect
from module_group.models import ModuleGroup, Module
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

# Logout view
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('main:login')  # Redirect to login page after logout

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')  # Redirect to home or dashboard if already logged in

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('main:home')  # Redirect to home or dashboard after login
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Home view (Dashboard)
@login_required
def home_view(request):
    modules = Module.objects.all()
    module_groups = ModuleGroup.objects.all()
    user_engagement_data = get_user_engagement_statistics(request.user)
    support_feedback_data = get_support_feedback_data(request.user)

    return render(request, 'home.html', {
        'module_groups': module_groups,
        'modules': modules,
        'user_engagement_data': user_engagement_data,
        'support_feedback_data': support_feedback_data,
    })


# Functions to get additional data for other tabs (this can be customized as needed)
def get_user_engagement_statistics(user):
    # Return dummy data for now (replace with actual logic)
    return {
        'courses_completed': 3,
        'time_spent': 45,  # hours
        'assignments_submitted': 7,
    }

def get_support_feedback_data(user):
    # Return dummy data for now (replace with actual logic)
    return [
        {'date': '2024-09-10', 'message': 'Great course!'},
        {'date': '2024-09-12', 'message': 'I had issues with module 3.'},
    ]
