from django.shortcuts import render, get_object_or_404, redirect
from .models import DiscussionThread, ThreadComments
from .forms import ThreadForm, CommentForm
from django.contrib.auth.decorators import login_required


def thread_list(request):
    threads = DiscussionThread.objects.all()
    return render(request, 'thread/thread_list.html', {'threads': threads})


@login_required  # Ensure only logged-in users can create threads
def createThread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.created_by = request.user  # Set the logged-in user as the creator
            thread.save()
            return redirect('thread:thread_list')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ThreadForm()

    return render(request, 'thread/thread_form.html', {'form': form})


@login_required
def updateThread(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    # Ensure only the thread creator can update the thread
    if request.user != thread.created_by and not request.user.is_superuser:
        return redirect('thread:thread_list')

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('thread:thread_list')
    else:
        form = ThreadForm(instance=thread)

    return render(request, 'thread/thread_form.html', {'form': form})


@login_required
def deleteThread(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    # Ensure only the thread creator can delete the thread
    if request.user != thread.created_by and not request.user.is_superuser:
        return redirect('thread:thread_list')

    if request.method == 'POST':
        thread.delete()
        return redirect('thread:thread_list')

    return render(request, 'thread/thread_confirm_delete.html', {'thread': thread})


def thread_detail(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)
    comments = thread.comments.all()  # Fetch all comments related to the thread
    form = CommentForm()  # Prepare an empty comment form
    return render(request, 'thread/thread_detail.html', {'thread': thread, 'comments': comments, 'form': form})


@login_required
def add_comment(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.user = request.user  # Set the logged-in user as the comment creator
            comment.save()
            return redirect('thread:thread_detail', pk=thread.pk)
    else:
        form = CommentForm()

    comments = thread.comments.all()  # Fetch all comments for the thread
    return render(request, 'thread/thread_detail.html', {'thread': thread, 'comments': comments, 'form': form})

@login_required
def update_comment(request, pk, comment_id):
    comment = get_object_or_404(ThreadComments, pk=comment_id)

    # Ensure only the comment author can update the comment
    if request.user != comment.user and not request.user.is_superuser:
        return redirect('thread:thread_detail', pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('thread:thread_detail', pk=pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'thread/comment_form.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, pk, comment_id):
    thread = get_object_or_404(DiscussionThread, pk=pk)
    comment = get_object_or_404(ThreadComments, pk=comment_id, thread=thread)

    # Ensure only the comment author can delete the comment
    if request.user != comment.user and not request.user.is_superuser:
        return redirect('thread:thread_detail', pk=thread.pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('thread:thread_detail', pk=thread.pk)

    return render(request, 'thread/comment_confirm_delete.html', {'comment': comment})

def moderation_warning(request):
    return render(request, 'thread/moderation_warning.html')