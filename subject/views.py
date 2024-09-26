from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, Document, Video, Enrollment, Prerequisite
from .forms import SubjectForm, DocumentForm, VideoForm, EnrollmentForm, SubjectSearchForm
from module_group.models import ModuleGroup
from django.contrib.auth.decorators import login_required
from subject.models import Document, Video
from django.db.models import Q
from django.contrib import messages
import os
from django.http import FileResponse,Http404
from django.utils.text import slugify
from django.urls import reverse
from feedback.models import CourseFeedback


@login_required
def subject_enroll(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            enrollment = form.save(commit=False)

            # Fetch prerequisites from the Prerequisite model
            prerequisites = Prerequisite.objects.filter(subject=subject)
            prerequisite_subjects = [prereq.prerequisite_subject for prereq in prerequisites]

            # Check if the user is enrolled in all prerequisite subjects
            if prerequisite_subjects:
                enrolled_subjects = Enrollment.objects.filter(
                    student=request.user,
                    subject__in=prerequisite_subjects
                ).values_list('subject', flat=True)

                # Ensure all prerequisites are met
                if not all(prereq.id in enrolled_subjects for prereq in prerequisite_subjects):
                    form.add_error(None, 'You do not meet the prerequisites for this course.')
                    return render(request, 'subject_enroll.html', {'form': form, 'subject': subject})

            # If prerequisites are met, save the enrollment
            enrollment.student = request.user
            enrollment.subject = subject
            enrollment.save()
            return redirect('subject:subject_list')
    else:
        form = EnrollmentForm()

    return render(request, 'subject_enroll.html', {'form': form, 'subject': subject})


@login_required
def subject_unenroll(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    try:
        enrollment = Enrollment.objects.get(student=request.user, subject=subject)
        enrollment.delete()
    except Enrollment.DoesNotExist:
        pass  # Có thể thêm thông báo lỗi nếu cần

    return redirect('subject:subject_list')


def subject_list(request):
    module_groups = ModuleGroup.objects.all()
    subjects = Subject.objects.all()
    enrollments = Enrollment.objects.filter(student=request.user)
    enrolled_subjects = {enrollment.subject.id for enrollment in enrollments}
    return render(request, 'subject_list.html', {
        'module_groups': module_groups,
      #  'modules': modules,
        'subjects': subjects,
        'enrolled_subjects': enrolled_subjects,
    })

def subject_add(request):
    if request.method == 'POST':
        subject_form = SubjectForm(request.POST)
        #doc_form = DocumentForm(request.POST, request.FILES)
        #vid_form = VideoForm(request.POST, request.FILES)

        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            subject.creator = request.user  # Gán người tạo là user hiện tại
            subject.save()

            # Handle multiple document uploads
            doc_files = request.FILES.getlist('doc_file[]')
            doc_titles = request.POST.getlist('doc_title[]')
            for file, title in zip(doc_files, doc_titles):
                if file and title:
                    Document.objects.create(
                        subject=subject,
                        doc_file=file,
                        doc_title=title
                    )

            # Handle multiple video uploads
            vid_files = request.FILES.getlist('vid_file[]')
            vid_titles = request.POST.getlist('vid_title[]')
            for file, title in zip(vid_files, vid_titles):
                if file and title:
                    Video.objects.create(
                        subject=subject,
                        vid_file=file,
                        vid_title=title
                    )
            # Handle prerequisite subjects
            prerequisite_ids = request.POST.getlist('prerequisite_subjects')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    Prerequisite.objects.create(subject=subject, prerequisite_subject=prerequisite_subject)

            messages.success(request, 'Subject created successfully.')
            return redirect('subject:subject_list')

        else:
            messages.error(request, 'There was an error creating the subject. Please check the form.')
    else:
        subject_form = SubjectForm()
        #doc_form = DocumentForm()
        #vid_form = VideoForm()
    all_subjects = Subject.objects.all()

    return render(request, 'subject_form.html', {
        'subject_form': subject_form,
        'all_subjects': all_subjects,
    })


# subject/views.py
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    all_subjects = Subject.objects.exclude(id=subject.id)

    if request.method == 'POST':
        subject_form = SubjectForm(request.POST, instance=subject)
        #doc_form = DocumentForm(request.POST, request.FILES)
        #vid_form = VideoForm(request.POST, request.FILES)

        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            subject.creator = request.user
            subject_form.save()

            documents = Document.objects.filter(subject=subject)
            for document in documents:
                if f'delete_document_{document.id}' in request.POST:
                    document.delete()

            videos = Video.objects.filter(subject=subject)
            for video in videos:
                if f'delete_video_{video.id}' in request.POST:
                    video.delete()

            # Handle multiple document uploads
            doc_files = request.FILES.getlist('doc_file[]')
            doc_titles = request.POST.getlist('doc_title[]')
            for file, title in zip(doc_files, doc_titles):
                if file and title:
                    Document.objects.create(
                        subject=subject,
                        doc_file=file,
                        doc_title=title
                    )

            # Handle multiple video uploads
            vid_files = request.FILES.getlist('vid_file[]')
            vid_titles = request.POST.getlist('vid_title[]')
            for file, title in zip(vid_files, vid_titles):
                if file and title:
                    Video.objects.create(
                        subject=subject,
                        vid_file=file,
                        vid_title=title
                    )

            # Handle deleting existing prerequisites
            prerequisites = Prerequisite.objects.filter(subject=subject)
            for prereq in prerequisites:
                if f'delete_prerequisite_{prereq.id}' in request.POST:
                    prereq.delete()

            # Handle adding new prerequisites
            prerequisite_ids = request.POST.getlist('prerequisite_subjects')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:  # Ensure the ID is not empty
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    Prerequisite.objects.create(subject=subject, prerequisite_subject=prerequisite_subject)

            messages.success(request, 'Subject updated successfully.')
            return redirect('subject:subject_list')
        else:
            messages.error(request, 'There was an error updating the subject. Please check the form.')
    else:
        subject_form = SubjectForm(instance=subject)
        #doc_form = DocumentForm()
        #vid_form = VideoForm()
        documents = Document.objects.filter(subject=subject)  # Chỉ lấy tài liệu
        videos = Video.objects.filter(subject=subject)
        prerequisites = Prerequisite.objects.filter(subject=subject)

    return render(request, 'edit_form.html', {
        'subject_form': subject_form,
        #'doc_form': doc_form,
        #'vid_form': vid_form,
        'documents': documents,
        'videos': videos,
        'subject': subject,
        'prerequisites': prerequisites,  # Pass prerequisites to the template
        'all_subjects': all_subjects,
    })


def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject:subject_list')
    return render(request, 'subject_confirm_delete.html', {'subject': subject})


def resource_library(request):
    documents = Document.objects.all()
    videos = Video.objects.all()
    return render(request, 'resource_library.html', {
        'documents': documents,
        'videos': videos,
    })


@login_required
def subject_detail(request, pk):
    # Get the subject based on the primary key (pk)
    subject = get_object_or_404(Subject, pk=pk)

    # Get related documents and videos
    documents = Document.objects.filter(subject=subject)
    videos = Video.objects.filter(subject=subject)
    is_enrolled = Enrollment.objects.filter(student=request.user, subject=subject).exists()
    users_enrolled_count = Enrollment.objects.filter(subject=subject).count()

    # Get all feedback related to the subject
    feedbacks = CourseFeedback.objects.filter(course=subject)

    # Calculate the subject's average rating
    if feedbacks.exists():
        total_rating = sum(feedback.average_rating() for feedback in feedbacks)
        subject_average_rating = total_rating / feedbacks.count()
    else:
        subject_average_rating = None  # No feedback yet

    # Get prerequisite subjects
    prerequisites = Prerequisite.objects.filter(subject=subject).select_related('prerequisite_subject')

    context = {
        'subject': subject,
        'documents': documents,
        'videos': videos,
        'prerequisites': prerequisites,
        'is_enrolled': is_enrolled,
        'users_enrolled_count': users_enrolled_count,
        'subject_average_rating': subject_average_rating,
        'feedbacks': feedbacks,  # Pass feedbacks to the template
    }

    return render(request, 'subject_detail.html', context)

def file_download(request, file_type, file_id):
    if file_type == 'document':
        file_obj = get_object_or_404(Document, id=file_id)
        file_path = file_obj.doc_file.path
        file_name = file_obj.doc_title
    elif file_type == 'video':
        file_obj = get_object_or_404(Video, id=file_id)
        file_path = file_obj.vid_file.path
        file_name = file_obj.vid_title
    else:
        raise Http404("File not found")

    file_extension = os.path.splitext(file_path)[1].lower()
    previewable_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg']

    if file_extension in previewable_extensions:
        # For previewable files, open them in the browser
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'inline; filename="{slugify(file_name)}{file_extension}"'
    else:
        # For non-previewable files, force download
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{slugify(file_name)}{file_extension}"'

    return response


def users_enrolled(request, pk):
    # Lấy môn học dựa trên khóa chính (primary key)
    subject = get_object_or_404(Subject, pk=pk)

    # Lấy danh sách người dùng đã đăng ký môn học
    enrolled_users = Enrollment.objects.filter(subject=subject).select_related('student')

    return render(request, 'users_subject_enrolled.html', {
        'subject': subject,
        'enrolled_users': enrolled_users,
    })

def course_search(request):
    form = SubjectSearchForm(request.GET or None)
    query = request.GET.get('query', '')
    courses = Subject.objects.all()

    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(subject_code__icontains=query))

    context = {
        'form': form,
        'subjects': courses,  # Make sure to pass 'subjects' instead of 'courses' for template consistency
    }
    return render(request, 'subject_list.html', context)

@login_required
def subject_content(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    documents = Document.objects.filter(subject=subject)
    videos = Video.objects.filter(subject=subject)

    preview_url = None
    download_url = None
    file_type = None
    content_type = None

    if 'file_id' in request.GET and 'file_type' in request.GET:
        file_id = request.GET['file_id']
        file_type = request.GET['file_type']

        if file_type == 'document':
            file_obj = get_object_or_404(Document, id=file_id, subject=subject)
            file_url = file_obj.doc_file.url
        elif file_type == 'video':
            file_obj = get_object_or_404(Video, id=file_id, subject=subject)
            file_url = file_obj.vid_file.url
        elif file_type == 'pdf':  # Thêm điều kiện cho PDF
            file_obj = get_object_or_404(Document, id=file_id, subject=subject)  # Giả sử tài liệu PDF cũng là Document
            file_url = file_obj.doc_file.url
        else:
            raise Http404("Invalid file type")

        file_name = os.path.basename(file_url)
        file_extension = os.path.splitext(file_name)[1].lower()

        previewable_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg', '.pdf', '.ppt', '.pptx']
        if file_extension in previewable_extensions:
            preview_url = file_url
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                content_type = 'image'
            elif file_extension in ['.mp4', '.webm', '.ogg']:
                content_type = 'video'
            elif file_extension == '.pdf':
                content_type = 'pdf'  # Thêm content type cho PDF
        else:
            download_url = reverse('subject:file_download', kwargs={'file_type': file_type, 'file_id': file_id})

    context = {
        'subject': subject,
        'documents': documents,
        'videos': videos,
        'preview_url': preview_url,
        'download_url': download_url,
        'file_type': file_type,
        'content_type': content_type,
    }

    return render(request, 'subject_content.html', context)
# In subject/views.py

@login_required
def subject_content_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    documents = Document.objects.filter(subject=subject)
    videos = Video.objects.filter(subject=subject)

    if request.method == 'POST':
        # Process documents
        for document in documents:
            if f'delete_document_{document.id}' in request.POST:
                document.delete()

        # Process videos
        for video in videos:
            if f'delete_video_{video.id}' in request.POST:
                video.delete()

        # Handle multiple document uploads
        doc_files = request.FILES.getlist('doc_file[]')
        doc_titles = request.POST.getlist('doc_title[]')
        for file, title in zip(doc_files, doc_titles):
            if file and title:  # Ensure both file and title are provided
                Document.objects.create(
                    subject=subject,
                    doc_file=file,
                    doc_title=title
                )

        # Handle multiple video uploads
        vid_files = request.FILES.getlist('vid_file[]')
        vid_titles = request.POST.getlist('vid_title[]')
        for file, title in zip(vid_files, vid_titles):
            if file and title:  # Ensure both file and title are provided
                Video.objects.create(
                    subject=subject,
                    vid_file=file,
                    vid_title=title
                )

        messages.success(request, 'Subject content updated successfully.')
        return redirect('subject:subject_content_edit', pk=subject.pk)

    return render(request, 'subject_content_edit.html', {
        'subject': subject,
        'documents': documents,
        'videos': videos,
    })
