from django.shortcuts import render, redirect, get_object_or_404
from module_group.models import ModuleGroup, Module
from django.contrib.auth import login
from django.urls import reverse
from .forms import UserRegistrationForm, NewsForm, EventForm
from .models import News, Event, UserProfile
from user.models import User
from user.forms import UserForm
from django.contrib.auth.models import User as AuthUser
from course.models import *

def home(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'home.html', {
        'module_groups': module_groups,
        'modules': modules,
        'enrollments': enrollments,
    })

def base_view(request):
    enrolled_courses = Enrollment.objects.filter(student=request.user).select_related('course')
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    return render(request, 'base.html', {
        'module_groups': module_groups,
        'modules': modules,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            user_form_data = {
                'username': cleaned_data['username'],
                'email': cleaned_data['email'],
                'full_name': cleaned_data['first_name'],
                'role': cleaned_data['role'],
                'password': cleaned_data['password1']
            }
            user_form = UserForm(data=user_form_data)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                password = user_form.cleaned_data['password']
                if not AuthUser.objects.filter(username=user.username).exists():
                    auth_user = AuthUser.objects.create_user(
                        username=user.username,
                        password=password,
                        email=user.email
                    )
                    user.auth_user = auth_user  # Link the auth_user instance to the custom User model
                else:
                    return render(request, 'user_form.html', {
                        'form': form,
                        'error_message': 'User with this username already exists in auth_user.',
                    })

            user.save()  # Save the custom User model instance

            return redirect('main:login')  # Redirect to login or another page
    else:
        form = UserRegistrationForm()

    return render(request, 'registration.html', {'form': form})

# View for the dashboard
def dashboard(request):
    news_list = News.objects.order_by('-created_at')[:5]  # Limit to 5 latest news
    event_list = Event.objects.order_by('event_date')[:5]  # Limit to upcoming events
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    return render(request, 'dashboard.html', {
        'news_list': news_list,
        'event_list': event_list,
        'module_groups': module_groups,
        'modules': modules,
    })

def dashboard_edit(request):
    news_list = News.objects.all()
    event_list = Event.objects.all()
    return render(request, 'dashboard_edit.html', {
        'news_list': news_list,
        'event_list': event_list,
    })

# Create and Edit News
def news_add(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main:dashboard')
    else:
        form = NewsForm()
    return render(request, 'news_form.html', {'form': form})

def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect('main:dashboard')
    else:
        form = NewsForm(instance=news)
    return render(request, 'news_form.html', {'form': form})

def delete_news(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    news_item.delete()
    return redirect(reverse('main:dashboard'))

# Create and Edit Event
def event_add(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main:dashboard')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form})

def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('main:dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form})

def delete_event(request, pk):
    event_item = get_object_or_404(Event, pk=pk)
    event_item.delete()
    return redirect(reverse('main:dashboard'))

def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {'news': news_item})

def event_detail(request, event_id):
    event_item = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event_item})

