"""
ASGI config for lms_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
#Đây là hàm Django cung cấp để tạo ra một ứng dụng ASGI (Asynchronous Server Gateway Interface)
#cho phép xử lý không chỉ các yêu cầu HTTP mà còn cả giao thức WebSocket và các giao thức khác.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

application = get_asgi_application()
#ASGI mà máy chủ ASGI sẽ sử dụng để giao tiếp với ứng dụng Django. 
# Nó hỗ trợ xử lý các yêu cầu bất đồng bộ (asynchronous), 
# thích hợp cho các ứng dụng thời gian thực như giao tiếp qua WebSocket.