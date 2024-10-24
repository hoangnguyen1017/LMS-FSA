from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [

    path('excel_to_json_view/',views.excel_to_json_view , name='excel_to_json_view'),

]