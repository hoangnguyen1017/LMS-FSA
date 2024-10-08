from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from user.models import Profile
from django.contrib.auth.models import User
import pandas as pd
import bcrypt
from django.http import HttpResponse
from django.contrib import messages
from user.forms import UserForm, RoleForm, ExcelImportForm
import openpyxl
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import AssignTrainingProgramForm, UserEditForm
from .decorators import role_required
from functools import wraps
from django.contrib.auth.decorators import login_required

@login_required
def assign_training_programs(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AssignTrainingProgramForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Training programs successfully assigned to {user.username}.")
            return redirect('user:user_list')
    else:
        form = AssignTrainingProgramForm(instance=user)

    return render(request, 'assign_training_programs.html', {'user': user, 'form': form})

@login_required
def user_list(request):
    query = request.GET.get('q', '')  
    selected_role = request.GET.get('role', '')  
    users = User.objects.exclude(is_superuser=True)  # Loại trừ superuser
    roles = Role.objects.all()  
    form = ExcelImportForm()  

    if query and selected_role:
        users = users.filter(
            Q(username__icontains=query),
            profile__role__role_name=selected_role 
        )
    elif query: 
        users = users.filter(username__icontains=query)
    elif selected_role: 
        users = users.filter(profile__role__role_name=selected_role)  

    not_found = not users.exists() 

    # Thêm order_by để sắp xếp trước khi phân trang
    users = users.order_by('username')  # Sắp xếp theo username

    paginator = Paginator(users, 5)
    page = request.GET.get('page', 1)  

    try:
        users = paginator.page(page)  
    except PageNotAnInteger:
        users = paginator.page(1)  
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  

    return render(request, 'user_list.html', {
        'users': users,
        'query': query,
        'roles': roles,
        'selected_role': selected_role,  
        'not_found': not_found,
        'form': form,  
    })

@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user_detail.html', {'user': user})

@login_required
def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user:user_list')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()
    return render(request, 'user_form.html', {'form': form})

@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Check access permissions
    if request.user.pk != user.pk and not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'Manager')):
        messages.error(request, "You do not have permission to edit this user.")
        return redirect('user:user_list')

    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        if request.user.pk == user.pk:  # Current user editing their own profile
            form = UserForm(request.POST, instance=user)
        elif request.user.is_superuser:  # Superuser can use UserForm
            form = UserForm(request.POST, instance=user)
        else:
            form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=True)  # Save user

            # Only superuser and manager can change role
            if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'Manager'):
                profile.role = form.cleaned_data.get('role')

            profile.profile_picture_url = form.cleaned_data.get('profile_picture_url')
            profile.bio = form.cleaned_data.get('bio', profile.bio)  # Keep old value if no new value
            profile.interests = form.cleaned_data.get('interests', profile.interests)  # Keep old value
            profile.learning_style = form.cleaned_data.get('learning_style', profile.learning_style)  # Keep old value
            profile.preferred_language = form.cleaned_data.get('preferred_language', profile.preferred_language)  # Keep old value
            profile.save()  # Save profile

            # Update session information if the current user is editing their own profile
            if request.user.pk == user.pk:
                request.session['username'] = user.username
                request.session['full_name'] = f"{user.first_name} {user.last_name}"
                request.session['role'] = profile.role.role_name if profile.role else 'No Role'
                request.session['profile_picture_url'] = profile.profile_picture_url
                request.session['bio'] = profile.bio
                request.session['interests'] = profile.interests
                request.session['learning_style'] = profile.learning_style
                request.session['preferred_language'] = profile.preferred_language

            messages.success(request, f"User {user.username} has been successfully updated.")
            return redirect('user:user_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        if request.user.is_superuser or request.user.pk == user.pk:
            form = UserForm(instance=user)
        else:
            form = UserEditForm(instance=user)

    # Pass existing profile data into the form
    form.fields['bio'].initial = profile.bio
    form.fields['interests'].initial = profile.interests
    form.fields['learning_style'].initial = profile.learning_style
    form.fields['preferred_language'].initial = profile.preferred_language
    form.fields['profile_picture_url'].initial = profile.profile_picture_url

    # Ensure the 'role' field is visible but non-editable for 'User' role
    form.fields['role'].initial = profile.role  # Show current role
    if hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'User':
        form.fields['role'].widget.attrs['disabled'] = True

    return render(request, 'user_form.html', {'form': form, 'user': user})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "delete successful!")
        return redirect('user:user_list')  

    return render(request, 'user_confirm_delete.html', {'user': user})


@login_required
@role_required(['Manager'])
def export_users(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=users.xlsx'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Users'

    columns = ['username', 'email', 'first_name', 'last_name', 'role', 'profile_picture_url', 'password', 'bio', 'interests', 'learning_style', 'preferred_language']
    worksheet.append(columns)

    # Lấy tất cả người dùng, bao gồm cả superuser nếu người dùng hiện tại là superuser
    if request.user.is_superuser:
        users = User.objects.all()  # Lấy tất cả người dùng
    else:
        users = User.objects.exclude(is_superuser=True)  # Loại trừ superuser

    for user in users:
        profile = Profile.objects.filter(user=user).first()  # Lấy profile của người dùng

        # Kiểm tra xem profile có tồn tại không
        if profile:
            role_name = profile.role.role_name if profile.role else 'No Role'
            profile_picture_url = profile.profile_picture_url if profile else 'No Image'
            bio = profile.bio if profile else 'N/A'
            interests = profile.interests if profile else 'N/A'
            learning_style = profile.learning_style if profile else 'N/A'
            preferred_language = profile.preferred_language if profile else 'N/A'
        else:
            # Nếu không có profile, gán giá trị mặc định cho các trường
            role_name = 'No Role'
            profile_picture_url = 'No Image'
            bio = 'N/A'
            interests = 'N/A'
            learning_style = 'N/A'
            preferred_language = 'N/A'

        password_hash = user.password

        worksheet.append([
            user.username, user.email, user.first_name, user.last_name,
            role_name, profile_picture_url, password_hash, bio, interests, learning_style, preferred_language
        ])

    workbook.save(response)
    return response


@login_required
@role_required(['Manager'])
def import_users(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        # Kiểm tra định dạng file
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Invalid file format. Please upload an .xlsx file.")
            return redirect('user:user_list')

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f"Error reading the Excel file: {e}")
            return redirect('user:user_list')

        # Duyệt qua từng dòng dữ liệu trong Excel
        for index, row in df.iterrows():
            username = row.get('username')
            email = row.get('email')
            first_name = row.get('first_name')
            last_name = row.get('last_name')
            role_name = row.get('role')
            password_hash = row.get('password')
            profile_picture_url = row.get('profile_picture_url')
            bio = row.get('bio')
            interests = row.get('interests')
            learning_style = row.get('learning_style')
            preferred_language = row.get('preferred_language')

            # Kiểm tra các trường cần thiết
            if not username or not email or not password_hash:
                messages.warning(request, f"Missing required fields for user at row {index + 1}. Skipping.")
                continue

            # Tạo hoặc lấy người dùng
            user, created = User.objects.get_or_create(username=username)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.password = password_hash  # Hash đã có sẵn
            user.save()

            # Xử lý Role và Profile của người dùng
            if role_name:
                role = Role.objects.filter(role_name=role_name).first()
                if role:
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = role
                    profile.profile_picture_url = profile_picture_url
                    profile.bio = bio if bio else 'N/A'  # Bổ sung bio
                    profile.interests = interests if interests else 'N/A'  # Bổ sung interests
                    profile.learning_style = learning_style if learning_style else 'N/A'  # Bổ sung learning_style
                    profile.preferred_language = preferred_language if preferred_language else 'N/A'  # Bổ sung preferred_language
                    profile.save()
                else:
                    messages.warning(request, f"Role '{role_name}' not found for user {username}.")
            else:
                messages.warning(request, f"User {username} has no role assigned.")

        messages.success(request, "Users imported successfully!")
        return redirect('user:user_list')

    messages.error(request, "Failed to import users.")

from django.contrib.auth.models import User
from openpyxl import Workbook

@login_required
@role_required(['Manager'])

def export_users(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=users.xlsx'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Users'

    # Thêm các cột tiêu đề
    columns = ['username', 'email', 'first_name', 'last_name', 'role', 'profile_picture_url', 'password', 'bio', 'interests', 'learning_style', 'preferred_language']
    worksheet.append(columns)

    # Lấy danh sách người dùng trừ superuser
    for user in User.objects.exclude(is_superuser=True):
        profile = Profile.objects.filter(user=user).first()
        role_name = profile.role.role_name if profile and profile.role else 'No Role'
        profile_picture_url = profile.profile_picture_url if profile else 'No Image'
        bio = profile.bio if profile else 'N/A'
        interests = profile.interests if profile else 'N/A'
        learning_style = profile.learning_style if profile else 'N/A'
        preferred_language = profile.preferred_language if profile else 'N/A'
        password_hash = user.password  # Hash mật khẩu của người dùng

        # Thêm dữ liệu của từng người dùng vào Excel
        worksheet.append([
            user.username, user.email, user.first_name, user.last_name,
            role_name, profile_picture_url, password_hash, bio, interests, learning_style, preferred_language
        ])

    workbook.save(response)
    return response



from django.contrib.auth.hashers import check_password

def user_edit_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        if check_password(old_password, user.password):
            return redirect('user:user_edit', user.pk)
        else:
            error_message = "Incorrect password. Please try again."
            return render(request, 'user_detail.html', {'user': user, 'error_message': error_message})

    return render(request, 'user_detail.html', {'user': user})