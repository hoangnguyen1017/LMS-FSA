from django.urls import path
from . import views

appname ="activity"
urlpatterns = [
    path('',views.activity_view,name = "activity view")
]