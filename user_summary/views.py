from django.shortcuts import render, redirect

def user_summary(request):
    return redirect('user_progress:user_progress_summary')