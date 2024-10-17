from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from .models import ProgressNotification
from .forms import ProgressNotificationForm

# User views
def progress_notification_list(request):
    progress_notification = ProgressNotification.objects.all()
    return render(request, 'progress_notification_list.html', {'progress_notification': progress_notification})

def progress_notification_detail(request, id):
    progress_notification = ProgressNotification.objects.get(id=id)
    return render(request, 'progress_notification_detail.html', {'progress_notification': progress_notification})

def progress_notification_add(request):
    if request.method == 'POST':
        form = ProgressNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('progress_notification:progress_notification_list')
    else:
        form = ProgressNotificationForm()
    return render(request, 'progress_notification_form.html', {'form': form})

def progress_notification_edit(request, id):
    progress_notification = get_object_or_404(ProgressNotification, id=id)
    print(progress_notification)
    if request.method == 'POST':
        form = ProgressNotificationForm(request.POST, instance=progress_notification)
        if form.is_valid():
            form.save()
            return redirect('progress_notification:progress_notification_list')
    else:
        form = ProgressNotificationForm(instance=progress_notification)
    return render(request, 'progress_notification_form.html', {'form': form})

def progress_notification_delete(request, id):
    notification = ProgressNotification.objects.get(id=id)
    if request.method == 'POST':
        notification.delete()
        return redirect('progress_notification:progress_notification_list')
    return render(request, 'progress_notification_confirm_delete.html', {'notification': notification})
