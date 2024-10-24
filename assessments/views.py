from django.shortcuts import render

# Create your views here.
def assessement_list(request):
    return render(request, 'assessment_list.html')