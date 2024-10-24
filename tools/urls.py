from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [

    path('excel_to_json_view/',views.excel_to_json_view , name='excel_to_json_view'),
    path('word_to_json_view/',views.word_to_json_view , name='word_to_json_view'),
    path('',views.view_tools , name="view_tools"),
]