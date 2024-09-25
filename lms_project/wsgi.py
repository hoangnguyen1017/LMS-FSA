"""
WSGI config for lms_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application #trả về một đối tượng WSGI -> điểm vào của ứng dụng Django cho bất kỳ server nào hỗ trợ WSGI

#'DJANGO_SETTINGS_MODULE' :biến môi trường mà Django sử dụng để xác định đường dẫn đến file cấu hình (settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

application = get_wsgi_application()
#Hàm này tạo ra một đối tượng WSGI, chính là ứng dụng Django được đóng gói dưới dạng WSGI