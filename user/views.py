from django.shortcuts import render, get_object_or_404, redirect
from .models import User
from .forms import UserForm
from module_group.models import ModuleGroup
from django.contrib.auth.models import User as AuthUser, Permission
import os
from django.conf import settings
from django.core.files.storage import default_storage
from subject.models import Enrollment

def authuser_to_role(user):
    username = user.username
    user = User.objects.get(username=username)
    user_role = user.role
    role_name=user_role.role_name
    return role_name

def user_list(request):
    if not request.user.is_superuser:
        return redirect('main:home')  # Redirect to the homepage if not superuser

    users = User.objects.all()
    module_groups = ModuleGroup.objects.all()
    return render(request, 'user_list.html', {
        'users': users,
        'module_groups': module_groups,
    })


def user_detail(request, pk):
    user = get_object_or_404(User, auth_user_id=pk)
    enrollments = Enrollment.objects.filter(student_id=user.auth_user_id)
    # Extract subject names
    subject_names = [enrollment.subject.name for enrollment in enrollments]

    return render(request, 'user_detail.html', {
        'user': user,
        'enrollments': enrollments,
        'subject_names': subject_names,
    })


def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            # Save the form data but don't commit to the database yet
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            cleaned_data = form.cleaned_data
            role_instance = cleaned_data['role']

            # Check for existing AuthUser
            if not AuthUser.objects.filter(username=user.username).exists():
                # Create the AuthUser based on the role
                if role_instance.role_name == 'Admin':
                    auth_user = AuthUser.objects.create_user(
                        username=user.username,
                        password=password,
                        email=user.email,
                        is_staff=True,
                        is_superuser=True
                    )
                elif role_instance.role_name == 'Staff':
                    auth_user = AuthUser.objects.create_user(
                        username=user.username,
                        password=password,
                        email=user.email,
                        is_staff=True,
                        is_superuser=False
                    )
                else:
                    auth_user = AuthUser.objects.create_user(
                        username=user.username,
                        password=password,
                        email=user.email,
                        is_staff=False,
                        is_superuser=False
                    )

                user.auth_user = auth_user
                user.save()  # Save the custom User model

                return redirect('user:user_list')
            else:
                # Handle the case where the username already exists
                form.add_error('username', 'This username is already taken. Please choose a different one.')
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form})


def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    old_image = user.profile_image
    auth_user = user.auth_user

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            updated_user = form.save(commit=False)
            password = form.cleaned_data.get('password')

            if password:  # Only update password if provided
                if auth_user:
                    auth_user.delete()
                    auth_user = AuthUser.objects.create_user(
                        username=updated_user.username,
                        password=password,
                        email=updated_user.email
                    )
                    updated_user.auth_user = auth_user

            # Handle the profile image deletion
            if 'profile_image' in request.FILES:
                # Only delete the old image if a new one is being uploaded
                if old_image and old_image.name != 'profile_images/default_profile.png':
                    old_image_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
                    if os.path.isfile(old_image_path):
                        default_storage.delete(old_image.name)  # Delete the old image

            updated_user.save()
            return redirect('user:user_list')
    else:
        form = UserForm(instance=user)

    return render(request, 'user_form.html', {'form': form})