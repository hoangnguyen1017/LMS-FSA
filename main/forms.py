
# main/forms.py
from django import forms
from django.contrib.auth.models import User  # Sử dụng model User của Django
from django.contrib.auth.hashers import make_password
from role.models import Role
from user.models import Profile
class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mật khẩu'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Xác nhận mật khẩu'}))
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên đầy đủ'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'}))

    class Meta:
        model = User  # Sử dụng model User mặc định của Django
        fields = ['username', 'email', 'password1', 'password2', 'full_name']  # Bao gồm email và tên đầy đủ
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên đăng nhập'}),

        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:

            raise forms.ValidationError("Mật khẩu không khớp")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)


        user.password = make_password(self.cleaned_data["password1"])  # Mã hóa mật khẩu
        user.first_name = self.cleaned_data['full_name']  # Lưu tên đầy đủ vào trường first_name
        user.email = self.cleaned_data['email']  # Lưu email

        if commit:
            user.save()
            user_role = Role.objects.get(role_name='User')  
            profile = Profile.objects.create(user=user, role=user_role)
        return user
    

from django import forms
from django.contrib.auth import authenticate

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid login credentials.")
        return cleaned_data


