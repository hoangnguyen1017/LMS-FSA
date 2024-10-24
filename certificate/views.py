from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Certificate

def certificate_list(request):
    certificates = Certificate.objects.all()

    return render(request, 'certificate.html', {'certificates': certificates})

@login_required
def certificate_pdf(request,id):
    certificate = Certificate.objects.get(id=id)
    context = {
        'certificate': certificate
    }
    return render(request, 'pdf.html', context)
