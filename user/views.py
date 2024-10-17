from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from .models import Profile, User, Student
import pandas as pd
import bcrypt
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib import messages
from user.forms import UserForm, RoleForm, ExcelImportForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import AssignTrainingProgramForm, UserEditForm
from .decorators import role_required
from functools import wraps
from django.contrib.auth.decorators import login_required
from django import forms
from course.forms import UserCourseProgress
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
def student_list(request):
    query = request.GET.get('q', '')  # Lấy từ khóa tìm kiếm từ request
    students = Student.objects.all()  # Lấy tất cả sinh viên
    form = ExcelImportForm()  # Form cho việc import Excel

    # Nếu có từ khóa tìm kiếm
    if query:
        students = students.filter(
            Q(user__username__icontains=query)   # Tìm theo full_name trong profile
        )

    # Sắp xếp theo username
    students = students.order_by('user__username')

    # Phân trang kết quả
    paginator = Paginator(students, 5)  # Hiển thị 5 sinh viên mỗi trang
    page = request.GET.get('page', 1)

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    return render(request, 'student_list.html', {
        'students': students,
        'query': query,
        'form': form,  # Form cho việc import (nếu cần)
    })
@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Lấy thông tin khóa học mà người dùng đã tham gia
    course_progress = UserCourseProgress.objects.filter(user=user)

    # Tạo một danh sách các khóa học cùng với tiến độ của chúng
    courses_with_progress = [
        {
            'course': progress.course,
            'progress_percentage': progress.progress_percentage
        }
        for progress in course_progress
    ]

    # Kiểm tra xem người dùng có phải là sinh viên không và lấy student_code
    is_student = request.user.is_authenticated and request.user.profile.role.role_name == 'Student'
    student_code = None
    if is_student:
        try:
            student = Student.objects.get(user=request.user)
            student_code = student.student_code
        except Student.DoesNotExist:
            student_code = None

    return render(request, 'user_detail.html', {
        'user': user,
        'courses_with_progress': courses_with_progress,
        'is_student': is_student,
        'student_code': student_code  # Truyền mã sinh viên vào template
    })

@login_required
def user_add(request):
    is_superuser = request.user.is_superuser  # Kiểm tra xem có phải superuser không

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Tạo đối tượng User nhưng chưa lưu vào cơ sở dữ liệu
            user.save()  # Lưu User
            
            # Tạo Profile cho User vừa tạo
            profile = Profile(
                user=user,
                role=form.cleaned_data['role'],
                profile_picture_url=form.cleaned_data.get('profile_picture_url', ''),
                bio=form.cleaned_data.get('bio', ''),
                interests=form.cleaned_data.get('interests', ''),
                learning_style=form.cleaned_data.get('learning_style', ''),
                preferred_language=form.cleaned_data.get('preferred_language', '')
            )
            profile.save()

            # Nếu vai trò là sinh viên, tạo bản ghi Student cho User đó
            if profile.role.role_name == 'Student':
                try:
                    # Lấy student_code từ form
                    student_code = form.cleaned_data.get('student_code')  
                    
                    # Tạo đối tượng Student và lưu vào cơ sở dữ liệu
                    student = Student(user=user, student_code=student_code)
                    student.save()  # Lưu đối tượng Student

                    # Cập nhật trường student trong Profile
                    profile.student = student
                    profile.save()
                except Exception as e:
                    print('Error saving Student:', e)  # In ra lỗi nếu có

            # Thêm chương trình đào tạo (training programs) nếu có
            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)  # Liên kết User với các chương trình đào tạo

            return redirect('user:user_list')  # Chuyển hướng đến danh sách người dùng
        else:
            print('Invalid form')  # In ra thông báo nếu form không hợp lệ
            print(form.errors)
    else:
        form = UserForm()  # Tạo form mới nếu không phải là POST
    
    return render(request, 'user_form.html', {'form': form, 'is_superuser': is_superuser})



@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Kiểm tra quyền truy cập
    if request.user.pk != user.pk and not (request.user.is_superuser or 
        (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'Manager')):
        messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
        return redirect('user:user_list')

    # Đảm bảo profile tồn tại
    profile, created = Profile.objects.get_or_create(user=user)

    # Lưu lại vai trò cũ
    old_role = profile.role

    # Lấy mã sinh viên nếu có
    student_code = None
    if profile.role.role_name == 'Student':
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code
        except Student.DoesNotExist:
            pass  # Không làm gì nếu bản ghi Student không tồn tại

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)  # Tạm thời lưu User để xử lý thêm
            user.save()  # Lưu User sau khi xử lý mật khẩu
            
            # Cập nhật thông tin Profile
            new_role = form.cleaned_data['role']  # Lấy vai trò mới từ form
            if new_role != old_role:  # Chỉ cập nhật nếu vai trò mới khác với vai trò cũ
                profile.role = new_role
            
            # Giữ lại URL ảnh đại diện cũ nếu không có giá trị mới
            new_profile_picture_url = form.cleaned_data.get('profile_picture_url')
            profile.profile_picture_url = new_profile_picture_url if new_profile_picture_url else profile.profile_picture_url
            
            profile.bio = form.cleaned_data.get('bio', profile.bio)
            profile.interests = form.cleaned_data.get('interests', profile.interests)
            profile.learning_style = form.cleaned_data.get('learning_style', profile.learning_style)
            profile.preferred_language = form.cleaned_data.get('preferred_language', profile.preferred_language)

            # Xử lý mối quan hệ Student
            if profile.role.role_name == 'Student':
                student, created = Student.objects.get_or_create(user=user)  # Tạo bản ghi Student nếu không tồn tại
                # Giữ mã sinh viên cũ nếu không có giá trị mới
                new_student_code = form.cleaned_data.get('student_code', student_code)
                student.student_code = new_student_code if new_student_code else student_code  # Cập nhật hoặc giữ mã sinh viên cũ
                student.save()  # Lưu student
                profile.student = student  # Liên kết student với profile
            else:
                # Nếu vai trò không phải là 'Student', xóa bản ghi Student nếu tồn tại
                try:
                    student = Student.objects.get(user=user)
                    student.delete()  # Xóa bản ghi Student
                    profile.student = None  # Ngắt liên kết student khỏi profile
                except Student.DoesNotExist:
                    pass  # Không làm gì nếu bản ghi Student không tồn tại
            
            profile.save()  # Lưu Profile với mối quan hệ student đã cập nhật
            user.save()  # Lưu User lại trong trường hợp có thay đổi
            
            # Cập nhật chương trình đào tạo nếu có
            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)  # Liên kết User với các chương trình đào tạo

            # Cập nhật thông tin phiên làm việc nếu người dùng hiện tại đang chỉnh sửa thông tin của mình
            if request.user.pk == user.pk:
                request.session['username'] = user.username
                request.session['full_name'] = f"{user.first_name} {user.last_name}"
                request.session['role'] = profile.role.role_name if profile.role else 'No Role'
                request.session['profile_picture_url'] = profile.profile_picture_url
                request.session['bio'] = profile.bio
                request.session['interests'] = profile.interests
                request.session['learning_style'] = profile.learning_style
                request.session['preferred_language'] = profile.preferred_language

            messages.success(request, f"Người dùng {user.username} đã được cập nhật thành công.")
            return redirect('user:user_list')
        else:
            messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
    else:
        form = UserForm(instance=user)

    # Pass existing profile data into the form
    form.fields['bio'].initial = profile.bio
    form.fields['interests'].initial = profile.interests
    form.fields['learning_style'].initial = profile.learning_style
    form.fields['preferred_language'].initial = profile.preferred_language
    form.fields['profile_picture_url'].initial = profile.profile_picture_url

    # Đảm bảo trường 'role' hiển thị nhưng không thể chỉnh sửa cho vai trò 'User'
    form.fields['role'].initial = profile.role  # Hiện thị vai trò hiện tại
    if hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'User':
        form.fields['role'].widget.attrs['disabled'] = True

    # Ẩn hoặc hiển thị trường 'student_code' dựa trên vai trò của người dùng
    if profile.role.role_name == 'Student':
        form.fields['student_code'].initial = student_code  # Điền giá trị student_code vào form
    else:
        form.fields['student_code'].widget = forms.HiddenInput()  # Ẩn trường student_code nếu không phải là Student

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

    # Lấy selected_role từ request GET
    selected_role = request.GET.get('role', '').strip()

    # Tạo tên file dựa trên role
    if selected_role:
        safe_role = "".join(c for c in selected_role if c.isalnum() or c in ['_', '-'])
        filename = f'{safe_role}.xlsx'  # Tên file có định dạng users_<role>.xlsx
    else:
        filename = 'users.xlsx'  # Tên file mặc định nếu không có role

    response['Content-Disposition'] = f'attachment; filename={filename}'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = f'{safe_role}' if selected_role else 'Users'

    # Cập nhật danh sách cột
    columns = ['Username', 'Email', 'First Name', 'Last Name', 'Role', 'Profile Picture', 'Password Hash', 'Bio', 'Interests', 'Learning Style', 'Preferred Language', 'Student Code']
    worksheet.append(columns)

    # Lấy tất cả người dùng, loại trừ superuser
    users = User.objects.exclude(is_superuser=True)

    # Lọc người dùng theo vai trò nếu có
    if selected_role:
        users = users.filter(profile__role__role_name=selected_role)

    for user in users:
        profile = Profile.objects.filter(user=user).first()  # Lấy profile của người dùng
        student = None

        # Kiểm tra xem người dùng có phải là sinh viên không
        if profile and profile.student:
            student = profile.student

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
        student_code = student.student_code if student else 'N/A'  # Lấy mã sinh viên nếu có

        worksheet.append([
            user.username, user.email, user.first_name, user.last_name,
            role_name, profile_picture_url, password_hash, bio, interests, learning_style, preferred_language, student_code
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
            username = row.get('Username')
            email = row.get('Email')
            first_name = row.get('First Name')
            last_name = row.get('Last Name')
            role_name = row.get('Role')
            password_hash = row.get('Password Hash')
            profile_picture_url = row.get('Profile Picture')
            bio = row.get('Bio')
            interests = row.get('Interests')
            learning_style = row.get('Learning Style')
            preferred_language = row.get('Preferred Language')
            student_code = row.get('Student Code')  # Mã sinh viên cho vai trò Student

            if not username or not email or not password_hash:
                messages.warning(request, f"Missing required fields for user at row {index + 1}. Skipping.")
                continue

            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': password_hash  # Nên mã hóa password trước khi lưu
            })

            profile = Profile.objects.filter(user=user).first()
            old_role_name = profile.role.role_name if profile and profile.role else None
            
            if not created:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.password = password_hash  # Nên mã hóa password trước khi lưu
                user.save()

            if role_name:
                role = Role.objects.filter(role_name=role_name).first()
                if role:
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = role
                    profile.profile_picture_url = profile_picture_url or 'No Image'
                    profile.bio = bio or 'N/A'
                    profile.interests = interests or 'N/A'
                    profile.learning_style = learning_style or 'N/A'
                    profile.preferred_language = preferred_language or 'N/A'
                    profile.save()

                    # Thêm bản ghi vào bảng Student nếu vai trò là 'Student'
                    if role_name == 'Student':
                        student, _ = Student.objects.get_or_create(user=user)
                        student.student_code = student_code or 'N/A'  # Gán mã sinh viên
                        student.save()
                        profile.student = student  # Lưu student_id vào profile
                        profile.save()  # Cập nhật profile với student_id
                else:
                    messages.warning(request, f"Role '{role_name}' not found for user {username}.")
            else:
                messages.warning(request, f"User {username} has no role assigned.")

            # Xóa bản ghi Student nếu vai trò không còn là 'Student'
            if old_role_name == 'Student' and profile.role.role_name != 'Student':
                try:
                    student = Student.objects.get(user=user)
                    student.delete()
                except Student.DoesNotExist:
                    pass

        messages.success(request, "Users imported successfully!")
        return redirect('user:user_list')

    messages.error(request, "Failed to import users.")
    return redirect('user:user_list')


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
