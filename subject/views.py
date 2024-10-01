from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, Document, Video, Enrollment, ReadingMaterial, Completion, SubjectMaterial
from .forms import SubjectForm, DocumentForm, VideoForm, EnrollmentForm, SubjectSearchForm
from module_group.models import ModuleGroup
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
import os
from django.http import FileResponse,Http404
from django.utils.text import slugify
from django.urls import reverse
from feedback.models import CourseFeedback
from .forms import ExcelImportForm
from django.http import HttpResponse
import openpyxl
import pandas as pd
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator


def export_subject(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_subject.xlsx'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Subject'

    # Define the columns
    columns = ['name', 'subject_code', 'description', 'creator', 'instructor']
    worksheet.append(columns)

    # Fetch all subjects and write to the Excel file
    for subject in Subject.objects.all():
        worksheet.append([
            subject.name,
            subject.subject_code,
            subject.description,
            subject.creator.username if subject.creator else 'N/A',  # Use username or other identifier
            subject.instructor.username if subject.instructor else 'N/A'  # Use username or other identifier
        ])

    workbook.save(response)
    return response


def import_subjects(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                subject_imported = 0
                subject_updated = 0

                for index, row in df.iterrows():
                    name = row['name']
                    subject_code = row['subject_code']
                    description = row['description']
                    creator_username = row['creator']
                    instructor_username = row['instructor']

                    print(f"Processing row: {name}")
                    # Fetch User instances
                    try:
                        creator = User.objects.get(username=creator_username)
                    except User.DoesNotExist:
                        messages.warning(request, f"Creator '{creator_username}' does not exist. Skipping subject '{name}'.")
                        continue

                    try:
                        instructor = User.objects.get(username=instructor_username)
                    except User.DoesNotExist:
                        messages.warning(request, f"Instructor '{instructor_username}' does not exist. Skipping subject '{name}'.")
                        continue

                    # Get or create the subject
                    subject, created = Subject.objects.get_or_create(
                        name=name,
                        defaults={
                            'subject_code': subject_code,
                            'description': description,
                            'creator': creator,
                            'instructor': instructor,
                        }
                    )

                    if created:
                        subject_imported += 1
                        print(f"Subject '{name}' created")
                    else:
                        subject_updated += 1
                        print(f"Subject '{name}' already exists and was not created")

                messages.success(request,
                                 f"{subject_imported} subjects imported successfully! {subject_updated} subjects already existed.")
            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")

            return redirect('subject:subject_list')
    else:
        form = ExcelImportForm()

    return render(request, 'subject_list.html', {'form': form})

@login_required
def subject_enroll(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            enrollment = form.save(commit=False)

            # Fetch prerequisite subjects from the Subject model
            prerequisite_subjects = subject.prerequisites.all()

            # Check if the user is enrolled in all prerequisite subjects
            if prerequisite_subjects.exists():
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
    if request.user.is_superuser:
        # Superuser can see all subjects
        subjects = Subject.objects.all()
    elif Subject.objects.filter(instructor=request.user).exists():
        # Instructors can see all subjects they are teaching, published or not
        subjects = Subject.objects.filter(
            Q(published=True) | Q(instructor=request.user)
        )
    else:
        subjects = Subject.objects.filter(published=True)  # Other users see only published subjects

    module_groups = ModuleGroup.objects.all()
    enrollments = Enrollment.objects.filter(student=request.user)
    enrolled_subjects = {enrollment.subject.id for enrollment in enrollments}

    # Pagination
    paginator = Paginator(subjects, 10)  # Show 10 subjects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'subject_list.html', {
        'module_groups': module_groups,
        'page_obj': page_obj,  # Pagination object for template
        'subjects': page_obj,  # Consistent with template expectations
        'enrolled_subjects': enrolled_subjects,  # To show enrolled status
    })

def subject_add(request):
    if request.method == 'POST':
        subject_form = SubjectForm(request.POST)
        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            subject.creator = request.user
            subject.save()

            # Handle prerequisite subjects
            prerequisite_ids = request.POST.getlist('prerequisite_subjects[]')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    subject.prerequisites.add(prerequisite_subject)

            messages.success(request, 'Subject created successfully.')
            return redirect('subject:subject_list')
        else:
            messages.error(request, 'There was an error creating the subject. Please check the form.')
    else:
        subject_form = SubjectForm()
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
        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            subject.creator = request.user
            subject_form.save()

            # Handle prerequisite subjects
            prerequisite_ids = request.POST.getlist('prerequisite_subjects[]')
            subject.prerequisites.clear()  # Clear the current prerequisites
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:  # Ensure the ID is not empty
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    subject.prerequisites.add(prerequisite_subject)

            messages.success(request, 'Subject updated successfully.')
            return redirect('subject:subject_list')
        else:
            messages.error(request, 'There was an error updating the subject. Please check the form.')
    else:
        subject_form = SubjectForm(instance=subject)
        prerequisites = subject.prerequisites.all()  # Get the prerequisites from the prerequisite column

    return render(request, 'edit_form.html', {
        'subject_form': subject_form,
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
    subjects = Subject.objects.all()

    selected_subject_id = request.GET.get('subject')
    if selected_subject_id:
        documents = documents.filter(subject_id=selected_subject_id)
        videos = videos.filter(subject_id=selected_subject_id)

    return render(request, 'resource_library.html', {
        'documents': documents,
        'videos': videos,
        'subjects': subjects,
        'selected_subject_id': selected_subject_id,
    })

@login_required
def subject_detail(request, pk):
    # Get the subject based on the primary key (pk)
    subject = get_object_or_404(Subject, pk=pk)

    # Get related documents and videos
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

    # Get prerequisite subjects directly from the subject's `prerequisites` column
    prerequisites = subject.prerequisites.all()

    context = {
        'subject': subject,
        'prerequisites': prerequisites,  # Pass prerequisites from the subject model
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

    # Add pagination for search results
    paginator = Paginator(courses, 10)  # Show 10 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,  # For paginated results
        'subjects': page_obj,  # Pass the paginated subjects as 'subjects' for template consistency
    }
    return render(request, 'subject_list.html', context)
@login_required
def subject_content(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    all_materials = SubjectMaterial.objects.filter(subject=subject).order_by('order')

    preview_url = None
    download_url = None
    file_type = None
    content_type = None
    file_id = None
    current_item = None
    next_item = None
    completion_status = False
    preview_content = None

    if 'file_id' in request.GET and 'file_type' in request.GET:
        file_id = request.GET.get('file_id')
        file_type = request.GET.get('file_type')

        if file_type == 'document':
            current_item = get_object_or_404(Document, id=file_id, subject=subject)
            file_url = current_item.doc_file.url
            content_type = 'document'
        elif file_type == 'video':
            current_item = get_object_or_404(Video, id=file_id, subject=subject)
            file_url = current_item.vid_file.url
            content_type = 'video'
        elif file_type == 'reading':
            current_item = get_object_or_404(ReadingMaterial, id=file_id, subject=subject)
            preview_url = True
            content_type = 'reading'
            preview_content = current_item.content

        # Find the next item
        current_material = all_materials.filter(material_id=file_id, material_type=file_type).first()
        if current_material:
            next_material = all_materials.filter(order__gt=current_material.order).first()
            if next_material:
                next_item = {
                    'type': next_material.material_type,
                    'id': next_material.material_id
                }

        # Check completion status
        completion = Completion.objects.filter(subject=subject, **{file_type: current_item}).first()
        completion_status = completion.completed if completion else False

        if file_type in ['document', 'video']:
            file_name = os.path.basename(file_url)
            file_extension = os.path.splitext(file_name)[1].lower()
            previewable_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg', '.pdf']
            if file_extension in previewable_extensions:
                preview_url = file_url
                if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                    content_type = 'image'
                elif file_extension in ['.mp4', '.webm', '.ogg']:
                    content_type = 'video'
                elif file_extension == '.pdf':
                    content_type = 'pdf'
            else:
                download_url = reverse('subject:file_download', kwargs={'file_type': file_type, 'file_id': file_id})

    context = {
        'subject': subject,
        'all_materials': all_materials,
        'preview_url': preview_url,
        'download_url': download_url,
        'file_type': file_type,
        'content_type': content_type,
        'file_id': file_id,
        'current_item': current_item,
        'next_item': next_item,
        'completion_status': completion_status,
        'preview_content': preview_content,
    }

    return render(request, 'subject_content.html', context)

@require_POST
@login_required
def toggle_completion(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    file_type = request.POST.get('file_type')
    file_id = request.POST.get('file_id')

    if file_type == 'document':
        content_object = get_object_or_404(Document, id=file_id, subject=subject)
    elif file_type == 'video':
        content_object = get_object_or_404(Video, id=file_id, subject=subject)
    elif file_type == 'reading':
        content_object = get_object_or_404(ReadingMaterial, id=file_id, subject=subject)
    else:
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    completion, created = Completion.objects.get_or_create(
        subject=subject,
        **{file_type: content_object}
    )
    completion.completed = not completion.completed
    completion.save()

    documents = list(Document.objects.filter(subject=subject).order_by('id'))
    videos = list(Video.objects.filter(subject=subject).order_by('id'))
    reading_materials = list(ReadingMaterial.objects.filter(subject=subject).order_by('id'))

    next_item_type = None
    next_item_id = None

    if file_type == 'document':
        current_index = documents.index(content_object)
        if current_index < len(documents) - 1:
            next_item = documents[current_index + 1]
            next_item_type = 'document'
            next_item_id = next_item.id
        elif videos:
            next_item = videos[0]
            next_item_type = 'video'
            next_item_id = next_item.id
        elif reading_materials:
            next_item = reading_materials[0]
            next_item_type = 'reading'
            next_item_id = next_item.id
    elif file_type == 'video':
        current_index = videos.index(content_object)
        if current_index < len(videos) - 1:
            next_item = videos[current_index + 1]
            next_item_type = 'video'
            next_item_id = next_item.id
        elif reading_materials:
            next_item = reading_materials[0]
            next_item_type = 'reading'
            next_item_id = next_item.id
    elif file_type == 'reading':
        current_index = reading_materials.index(content_object)
        if current_index < len(reading_materials) - 1:
            next_item = reading_materials[current_index + 1]
            next_item_type = 'reading'
            next_item_id = next_item.id

    return JsonResponse({
        'completed': completion.completed,
        'next_item_type': next_item_type,
        'next_item_id': next_item_id
    })
# In subject/views.py

@login_required
def subject_content_edit(request, pk):
    order = 1
    subject = get_object_or_404(Subject, pk=pk)
    documents = Document.objects.filter(subject=subject)
    videos = Video.objects.filter(subject=subject)
    reading_materials = ReadingMaterial.objects.filter(subject=subject)

    if request.method == 'POST':
        # Process documents
        for document in documents:
            if f'delete_document_{document.id}' in request.POST:
                document.delete()

        # Process videos
        for video in videos:
            if f'delete_video_{video.id}' in request.POST:
                video.delete()

        # Process reading materials for deletion
        for reading_material in reading_materials:
            if f'delete_reading_material_{reading_material.id}' in request.POST:
                reading_material.delete()

        # Handle multiple document uploads
        doc_files = request.FILES.getlist('doc_file[]')
        doc_titles = request.POST.getlist('doc_title[]')
        for file, title in zip(doc_files, doc_titles):
            if file and title:
                document = Document.objects.create(
                    subject=subject,
                    doc_file=file,
                    doc_title=title
                )
                SubjectMaterial.objects.create(
                    subject=subject,
                    material_id=document.id,
                    material_type='document',
                    title=document.doc_title,  # Changed from document.title to document.doc_title
                    order=order
                )
            order += 1

        # Handle multiple video uploads
        vid_files = request.FILES.getlist('vid_file[]')
        vid_titles = request.POST.getlist('vid_title[]')
        for file, title in zip(vid_files, vid_titles):
            if file and title:
                video = Video.objects.create(
                    subject=subject,
                    vid_file=file,
                    vid_title=title
                )
                SubjectMaterial.objects.create(
                    subject=subject,
                    material_id=video.id,
                    material_type='video',
                    title=video.vid_title,  # Changed from video.title to video.vid_title
                    order=order
                )
            order += 1

        # Handle reading materials
        reading_material_titles = request.POST.getlist('reading_material_title[]')
        reading_material_contents = request.POST.getlist('reading_material_content[]')
        for title, content in zip(reading_material_titles, reading_material_contents):
            if title and content:
                reading_material = ReadingMaterial.objects.create(
                    subject=subject,
                    title=title,
                    content=content
                )
                SubjectMaterial.objects.create(
                    subject=subject,
                    material_id=reading_material.id,
                    material_type='reading',
                    title=reading_material.title,
                    order=order
                )
            order += 1

        messages.success(request, 'Subject content updated successfully.')
        return redirect('subject:subject_content_edit', pk=subject.pk)

    return render(request, 'subject_content_edit.html', {
        'subject': subject,
        'documents': documents,
        'videos': videos,
        'reading_materials': reading_materials,  # Pass reading materials to the template
    })

@login_required
def toggle_publish(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.user == subject.instructor or request.user.is_superuser:
        subject.published = not subject.published
        subject.save()
    return redirect('subject:subject_detail', pk=pk)