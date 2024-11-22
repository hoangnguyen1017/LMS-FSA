from django.test import TestCase, Client
from django.urls import reverse
from user.models import User, Profile, Student
from role.models import Role
from django.contrib.messages import get_messages

class UserAddViewTest(TestCase):

    def setUp(self):
        # Tạo role
        self.role_student = Role.objects.create(role_name='Student')
        self.role_manager = Role.objects.create(role_name='Manager')

        # Tạo superuser
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='123456'
        )

        # Tạo người dùng thường với profile
        self.user_with_profile = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='test123'
        )
        self.profile = Profile.objects.create(user=self.user_with_profile, role=self.role_student)

        # URL cho view
        self.url = reverse('user:user_add')

        # Client để gửi request
        self.client = Client()

    def test_user_add_no_permission(self):
        # Đăng nhập với người dùng không có quyền
        self.client.login(username='testuser', password='test123')
        response = self.client.get(self.url)

        # Kiểm tra phản hồi và thông báo lỗi
        self.assertRedirects(response, reverse('user:user_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Bạn không có quyền.")

    def test_user_add_superuser_access(self):
        # Đăng nhập với superuser
        self.client.login(username='admin', password='123456')
        response = self.client.get(self.url)

        # Kiểm tra hiển thị form
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_form.html')

    def test_user_add_valid_data(self):
        # Đăng nhập với superuser
        self.client.login(username='admin', password='123456')

        # Dữ liệu hợp lệ để thêm người dùng
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'role': self.role_student.id,
            'password1': 'StrongP@ssw0rd',
            'password2': 'StrongP@ssw0rd',
            'profile_picture_url': 'http://example.com/pic.jpg',
            'bio': 'New user bio',
            'interests': 'Coding, Reading',
            'learning_style': 'Visual',
            'preferred_language': 'English',
            'student_code': 'S12345'
        }

        response = self.client.post(self.url, data)

        # Kiểm tra người dùng được tạo
        self.assertRedirects(response, reverse('user:user_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.profile.bio, 'New user bio')
        self.assertTrue(Student.objects.filter(user=user, student_code='S12345').exists())

    def test_user_add_invalid_data(self):
        # Đăng nhập với superuser
        self.client.login(username='admin', password='123456')

        # Dữ liệu không hợp lệ (password không khớp)
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'role': self.role_student.id,
            'password1': 'StrongP@ssw0rd',
            'password2': 'WeakPass',
        }

        response = self.client.post(self.url, data)

        # Kiểm tra form báo lỗi
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match.")
        self.assertFalse(User.objects.filter(username='newuser').exists())
