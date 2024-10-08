from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, Document, Video, Enrollment, ReadingMaterial, Completion, SubjectMaterial, Session
from .forms import SubjectForm, DocumentForm, VideoForm, EnrollmentForm, SubjectSearchForm, SessionForm
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
from django.template.loader import get_template
from io import BytesIO
from datetime import datetime
import base64


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

    # Calculate completion percentage for each subject
    for subject in subjects:
        subject.completion_percent = subject.get_completion_percent(request.user)

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
            # Save the Subject
            subject = subject_form.save(commit=False)
            subject.creator = request.user
            subject.save()

            # Handle prerequisite subjects (optional)
            prerequisite_ids = request.POST.getlist('prerequisite_subjects[]')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    subject.prerequisites.add(prerequisite_subject)

            # Create sessions for the subject directly
            session_name = request.POST.get('session_name')
            session_quantity = int(request.POST.get('session_quantity', 0))
            if session_name and session_quantity > 0:
                for i in range(1, session_quantity + 1):
                    session = Session(
                        subject=subject,
                        name=f"{session_name}{i}",
                        order=i
                    )
                    session.save()

            messages.success(request, 'Subject and sessions created successfully.')
            return redirect('subject:subject_list')
        else:
            messages.error(request, 'There was an error creating the subject. Please check the form.')

    else:
        subject_form = SubjectForm()
        session_form = SessionForm()

    all_subjects = Subject.objects.all()

    return render(request, 'subject_form.html', {
        'subject_form': subject_form,
        'session_form': session_form,
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
            subject.save()

            # Handle prerequisite deletion
            current_prerequisites = list(subject.prerequisites.all())
            for prereq in current_prerequisites:
                if request.POST.get(f'delete_prerequisite_{prereq.id}'):
                    subject.prerequisites.remove(prereq)

            # Handle adding new prerequisites
            prerequisite_ids = request.POST.getlist('prerequisite_subjects')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_subject = Subject.objects.get(id=prerequisite_id)
                    subject.prerequisites.add(prerequisite_subject)

            # Handle sessions update
            session_ids = request.POST.getlist('session_ids')
            session_names = request.POST.getlist('session_names')
            for session_id, session_name in zip(session_ids, session_names):
                session = Session.objects.get(id=session_id)
                session.name = session_name
                session.save()

            # Handle adding new sessions
            new_session_names = request.POST.getlist('new_session_names')
            for session_name in new_session_names:
                if session_name:
                    Session.objects.create(subject=subject, name=session_name, order=subject.sessions.count() + 1)

            # Handle session deletion
            delete_session_ids = request.POST.getlist('delete_session_ids')
            for session_id in delete_session_ids:
                Session.objects.filter(id=session_id).delete()

            messages.success(request, 'Subject updated successfully.')
            return redirect('subject:subject_list')
        else:
            messages.error(request, 'There was an error updating the subject. Please check the form.')

    else:
        subject_form = SubjectForm(instance=subject)
        prerequisites = subject.prerequisites.all()
        sessions = subject.sessions.all()

    return render(request, 'edit_form.html', {
        'subject_form': subject_form,
        'subject': subject,
        'prerequisites': prerequisites,
        'all_subjects': all_subjects,
        'sessions': sessions,  # Pass sessions to template
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

    sessions = Session.objects.filter(subject=subject)

    context = {
        'subject': subject,
        'prerequisites': prerequisites,  # Pass prerequisites from the subject model
        'is_enrolled': is_enrolled,
        'users_enrolled_count': users_enrolled_count,
        'subject_average_rating': subject_average_rating,
        'feedbacks': feedbacks,  # Pass feedbacks to the template
        'sessions': sessions,
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
def reorder_subject_materials(request, pk, session_id):
    # Fetch the subject
    subject = get_object_or_404(Subject, pk=pk)

    # Fetch all sessions related to the subject
    sessions = Session.objects.filter(subject=subject)

    # Fetch materials for the selected session, defaulting to the first session
    selected_session_id = request.POST.get('session_id') or session_id
    session = get_object_or_404(Session, id=selected_session_id)
    materials = SubjectMaterial.objects.filter(session=session).order_by('order')

    if request.method == 'POST':
        # Check if the request is for reordering materials
        if 'order' in request.POST:
            for material in materials:
                new_order = request.POST.get(f'order_{material.id}')
                if new_order:
                    material.order = int(new_order)  # Convert to integer
                    material.save()

            success_message = "Order updated successfully!"
            return render(request, 'reorder_subject_material.html', {
                'subject': subject,
                'sessions': sessions,
                'materials': materials,
                'selected_session_id': selected_session_id,
                'success_message': success_message,
            })

    # Pass the subject, sessions, and materials to the template
    return render(request, 'reorder_subject_material.html', {
        'subject': subject,
        'sessions': sessions,
        'materials': materials,
        'selected_session_id': selected_session_id,
    })
def reading_material_detail(request, id):
    # Fetch the reading material by ID or return a 404 if it doesn't exist
    reading_material = get_object_or_404(ReadingMaterial, id=id)
    return render(request, 'reading_material_detail.html', {'reading_material': reading_material})

@login_required
def subject_content(request, pk, session_id):
    subject = get_object_or_404(Subject, pk=pk)
    sessions = Session.objects.filter(subject=subject)

    # Fetch materials for the selected session
    selected_session_id = request.POST.get('session_id') or session_id
    session = get_object_or_404(Session, id=selected_session_id)
    materials = SubjectMaterial.objects.filter(session=session).order_by('order')

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
            current_item = get_object_or_404(Document, id=file_id)
            file_url = current_item.doc_file.url
            content_type = 'document'
        elif file_type == 'video':
            current_item = get_object_or_404(Video, id=file_id)
            file_url = current_item.vid_file.url
            content_type = 'video'
        elif file_type == 'reading':
            current_item = get_object_or_404(ReadingMaterial, id=file_id)
            preview_url = True
            content_type = 'reading'
            preview_content = current_item.content

        # Find the next item
        current_material = materials.filter(material_id=file_id, material_type=file_type).first()
        if current_material:
            next_material = materials.filter(order__gt=current_material.order).first()
            if next_material:
                next_item = {
                    'type': next_material.material_type,
                    'id': next_material.material_id
                }

        # Check completion status
        completion = Completion.objects.filter(session=session, material__material_id=current_item.id, material__material_type=file_type).first()
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

    # Calculate completion percentage based on all materials
    all_materials = SubjectMaterial.objects.filter(session__subject=subject)  # Fetch all materials across all sessions
    total_materials = all_materials.count()
    completed_materials = Completion.objects.filter(
        session__subject=subject,
        completed=True
    ).count()

    completion_percent = (completed_materials / total_materials) * 100 if total_materials > 0 else 0

    # Check if the course is completed and generate certificate
    certificate_url = None
    if completion_percent == 100:
        certificate_url = reverse('subject:generate_certificate', kwargs={'pk': subject.pk})

    context = {
        'subject': subject,
        'sessions': sessions,
        'materials': materials,  # Only show materials from the selected session
        'preview_url': preview_url,
        'download_url': download_url,
        'file_type': file_type,
        'content_type': content_type,
        'file_id': file_id,
        'current_item': current_item,
        'next_item': next_item,
        'completion_status': completion_status,
        'preview_content': preview_content,
        'certificate_url': certificate_url,
        'selected_session_id': selected_session_id,
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
def subject_content_edit(request, pk, session_id):
    order = 1
    subject = get_object_or_404(Subject, pk=pk)
    sessions = Session.objects.filter(subject=subject)

    # Default to the first session if not specified in POST
    selected_session_id = request.POST.get('session_id') or session_id
    session = get_object_or_404(Session, id=selected_session_id)

    # Fetch materials associated with the selected session
    materials = SubjectMaterial.objects.filter(session=session)
    #print("Materials associated with selected session:", [vars(material) for material in materials])  # List comprehension for material attributes

    # Get documents, videos, and reading materials based on the filtered materials
    document_ids = materials.filter(material_type='document').values_list('material_id', flat=True)
    video_ids = materials.filter(material_type='video').values_list('material_id', flat=True)
    reading_ids = materials.filter(material_type='reading').values_list('material_id', flat=True)

    documents = Document.objects.filter(id__in=document_ids)
    videos = Video.objects.filter(id__in=video_ids)
    reading_materials = ReadingMaterial.objects.filter(id__in=reading_ids)

    if request.method == 'POST':
        print("Session ID POST:", request.POST.get('session_id'))  # Debugging line
        # Process documents for deletion
        for document in documents:
            if f'delete_document_{document.id}' in request.POST:
                document.delete()

        # Process videos for deletion
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
                    #material=None,  # Set the material reference later
                    doc_file=file,
                    doc_title=title
                )
                # Create a SubjectMaterial instance for the document
                subject_material = SubjectMaterial.objects.create(
                    session=session,
                    material_id=document.id,
                    material_type='document',
                    title=document.doc_title,
                    order=order
                )
                document.material = subject_material  # Set the reverse relationship
                document.save()
                order += 1

        # Handle multiple video uploads
        vid_files = request.FILES.getlist('vid_file[]')
        vid_titles = request.POST.getlist('vid_title[]')
        for file, title in zip(vid_files, vid_titles):
            if file and title:
                video = Video.objects.create(
                    #material=None,  # Set the material reference later
                    vid_file=file,
                    vid_title=title
                )
                # Create a SubjectMaterial instance for the video
                subject_material = SubjectMaterial.objects.create(
                    session=session,
                    material_id=video.id,
                    material_type='video',
                    title=video.vid_title,
                    order=order
                )
                video.material = subject_material  # Set the reverse relationship
                video.save()
                order += 1

        # Handle reading materials
        reading_material_titles = request.POST.getlist('reading_material_title[]')
        reading_material_contents = request.POST.getlist('reading_material_content[]')
        for title, content in zip(reading_material_titles, reading_material_contents):
            if title and content:
                reading_material = ReadingMaterial.objects.create(
                    material=None,  # Set the material reference later
                    title=title,
                    content=content
                )
                # Create a SubjectMaterial instance for the reading material
                subject_material = SubjectMaterial.objects.create(
                    session=session,
                    material_id=reading_material.id,
                    material_type='reading',
                    title=reading_material.title,
                    order=order
                )
                reading_material.material = subject_material  # Set the reverse relationship
                reading_material.save()
                order += 1

        messages.success(request, 'Subject content updated successfully.')
        return redirect(reverse('subject:subject_content_edit', args=[subject.pk, session.id]))

    # Context to render the template
    context = {
        'subject': subject,
        'sessions': sessions,
        'selected_session': session,
        'documents': documents,
        'videos': videos,
        'reading_materials': reading_materials,
    }

    return render(request, 'subject_content_edit.html', context)

@login_required
def toggle_publish(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.user == subject.instructor or request.user.is_superuser:
        subject.published = not subject.published
        subject.save()
    return redirect('subject:subject_detail', pk=pk)

@login_required
def generate_certificate_png(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    student = request.user

    # Verify that the student has completed the course
    total_materials = SubjectMaterial.objects.filter(subject=subject).count()
    completed_materials = Completion.objects.filter(
        subject=subject,
        completed=True
    ).filter(
        Q(document__subject=subject) |
        Q(video__subject=subject) |
        Q(reading__subject=subject)
    ).distinct().count()

    if completed_materials != total_materials:
        return HttpResponse("You have not completed this course yet.", status=403)

    # Dynamically find the background image in the subject app's static directory
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root of the project
    background_image_path = os.path.join(app_dir, 'subject', 'static', 'subject', 'images', 'certificate_background.jpg')

    if os.path.exists(background_image_path):
        with open(background_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
    else:
        return HttpResponse(f"Background image not found at {background_image_path}", status=500)

    # Generate the certificate
    context = {
        'student_name': student.get_full_name() or student.username,
        'course_name': subject.name,
        'completion_date': datetime.now().strftime("%B %d, %Y"),
        'background_image_base64': encoded_string,
    }

    return render(request, 'certificate_template.html', context)

