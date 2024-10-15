from django.urls import path,include
from .views import *
app_name = 'performance_analytics'
urlpatterns = [
    path('base/',view=base_view,name='base'),
    path('',view=performance_analytics_view,name='performance_analytics')
    
    
]