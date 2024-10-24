from django.urls import path
from . import views

app_name = 'certificate'

urlpatterns = [
    path('', views.certificate_list, name='certificate_list'),
    path('pdf/<int:id>/', views.certificate_pdf, name='certificate_pdf'),
]

