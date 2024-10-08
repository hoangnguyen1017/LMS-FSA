from django.shortcuts import render, redirect

from .forms import RegistrationForm, CustomLoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from module_group.models import Module, ModuleGroup
from django.db.models import Q
from module_group.forms import ExcelImportForm
from django.contrib.auth.decorators import login_required
# from user.views import login_required
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Đăng nhập ngay sau khi đăng ký
            return redirect('main:login')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Xác thực người dùng
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Đăng nhập người dùng và Django sẽ tự lưu thông tin vào session
                login(request, user)

                # Gửi thông báo đăng nhập thành công
                messages.success(request, "Login successful!")
                
                # Chuyển hướng về trang chính hoặc trang người dùng yêu cầu trước đó
                next_url = request.GET.get('next', 'main:home')
                return redirect(next_url)
            else:
                # Thông báo lỗi nếu username hoặc password không đúng
                messages.error(request, "Invalid username or password.")
        else:
            # Thông báo lỗi nếu form không hợp lệ
            messages.error(request, "Form is not valid.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})
    

from django.contrib import messages
@login_required  # Đảm bảo người dùng đã đăng nhập
def home(request):
    query = request.GET.get('q')

    # Lấy tất cả các module
    all_modules = Module.objects.all()

    # Kiểm tra vai trò của người dùng và quyền superuser
    if request.user.is_authenticated:
        try:
            # Lấy role của người dùng
            user_profile = getattr(request.user, 'profile', None)
            user_role = getattr(user_profile, 'role', None)

            if request.user.is_superuser or (user_role and user_role.role_name == "Manager"):
                # Manager và superuser có thể xem tất cả các module
                modules = all_modules
            elif user_role and user_role.role_name == 'User':
                # User chỉ xem một số module nhất định
                modules = all_modules.filter(module_name__in=['Course list', 'User', 'Subject', 'Quiz'])
            else:
                # Nếu không có vai trò hợp lệ, không hiển thị module nào
                messages.error(request, "Invalid role or no modules available for this role.")
                modules = Module.objects.none()
        except AttributeError:
            # Trường hợp không tìm thấy profile
            messages.error(request, "User profile not found.")
            modules = Module.objects.none()
    else:
        # Nếu người dùng chưa đăng nhập, không hiển thị module nào
        modules = Module.objects.none()

    # Lọc theo từ khóa tìm kiếm nếu có
    if query:
        modules = modules.filter(
            Q(module_name__icontains=query) |
            Q(module_group__group_name__icontains=query)
        )

    # Lấy tất cả các module groups để hiển thị
    module_groups = ModuleGroup.objects.all()
    form = ExcelImportForm()

    return render(request, 'home.html', {
        'module_groups': module_groups,
        'modules': modules,
        'form': form,
    })






