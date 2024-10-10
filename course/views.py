from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, ReadingMaterial, Completion, Session, SessionCompletion
from .forms import CourseForm, EnrollmentForm, CourseSearchForm, SessionForm
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
from datetime import datetime
import base64
from itertools import zip_longest
import numpy as np


def export_course(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_course.xlsx'

    workbook = openpyxl.Workbook()

    # Course sheet
    course_worksheet = workbook.active
    course_worksheet.title = 'Course'
    course_columns = ['name', 'course_code', 'description', 'creator', 'instructor', 'published', 'prerequisites']
    course_worksheet.append(course_columns)

    for course in Course.objects.all():
        prerequisites_list = ', '.join([prerequisite.name for prerequisite in course.prerequisites.all()]) or None
        course_worksheet.append([
            course.name,
            course.course_code,
            course.description,
            course.creator.username if course.creator else None,
            course.instructor.username if course.instructor else None,
            course.published,
            prerequisites_list
        ])

    # Session sheet
    session_worksheet = workbook.create_sheet(title='Session')
    session_columns = ['session_id', 'course_name', 'session_name', 'session_order']
    session_worksheet.append(session_columns)

    for session in Session.objects.all():
        session_worksheet.append([
            session.id,  # Include session ID
            session.course.name if session.course else None,
            session.name,
            session.order
        ])

    workbook.save(response)
    return response

def to_none_if_nan(value):
    """Convert value to None if it is NaN."""
    return None if isinstance(value, float) and np.isnan(value) else value

def import_courses(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                # Read necessary sheets
                course_df = pd.read_excel(uploaded_file, sheet_name='Course')
                session_df = pd.read_excel(uploaded_file, sheet_name='Session')

                # Import courses
                course_imported = 0
                course_updated = 0

                for index, row in course_df.iterrows():
                    name = row['name']
                    course_code = row['course_code']
                    description = row['description']
                    creator_username = to_none_if_nan(row.get('creator'))
                    instructor_username = to_none_if_nan(row.get('instructor'))
                    prerequisites = to_none_if_nan(row.get('prerequisites'))

                    # Fetch User instances
                    creator = User.objects.filter(username=creator_username).first() if creator_username else None
                    instructor = User.objects.filter(username=instructor_username).first() if instructor_username else None

                    # Get or create the course
                    course, created = Course.objects.get_or_create(
                        name=name,
                        defaults={
                            'course_code': course_code,
                            'description': description,
                            'creator': creator,
                            'instructor': instructor,
                        }
                    )

                    if created:
                        course_imported += 1
                    else:
                        course_updated += 1

                    # Handle prerequisites
                    if prerequisites:
                        prerequisite_names = [prerequisite.strip() for prerequisite in prerequisites.split(',')]
                        course.prerequisites.clear()
                        for prerequisite_name in prerequisite_names:
                            prerequisite = Course.objects.filter(name=prerequisite_name).first()
                            if prerequisite:
                                course.prerequisites.add(prerequisite)
                            else:
                                messages.warning(request, f"Prerequisite '{prerequisite_name}' does not exist for course '{name}'.")

                # Import sessions
                for index, row in session_df.iterrows():
                    course_name = row['course_name']
                    session_name = row['session_name']
                    session_order = row['session_order']

                    course = Course.objects.filter(name=course_name).first()
                    if course:
                        Session.objects.get_or_create(
                            course=course,
                            name=session_name,
                            defaults={'order': session_order}
                        )

                messages.success(request, f"{course_imported} courses imported successfully! {course_updated} courses already existed.")
            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")

            return redirect('course:course_list')
    else:
        form = ExcelImportForm()

    return render(request, 'course_list.html', {'form': form})


@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            enrollment = form.save(commit=False)

            # Fetch prerequisite courses from the Course model
            prerequisite_courses = course.prerequisites.all()

            # Check if the user is enrolled in all prerequisite courses
            if prerequisite_courses.exists():
                enrolled_courses = Enrollment.objects.filter(
                    student=request.user,
                    course__in=prerequisite_courses
                ).values_list('course', flat=True)

                # Ensure all prerequisites are met
                if not all(prereq.id in enrolled_courses for prereq in prerequisite_courses):
                    form.add_error(None, 'You do not meet the prerequisites for this course.')
                    return render(request, 'course_enroll.html', {'form': form, 'course': course})

            # If prerequisites are met, save the enrollment
            enrollment.student = request.user
            enrollment.course = course
            enrollment.save()
            return redirect('course:course_list')
    else:
        form = EnrollmentForm()

    return render(request, 'course_enroll.html', {'form': form, 'course': course})


@login_required
def course_unenroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        enrollment.delete()
    except Enrollment.DoesNotExist:
        pass  # Có thể thêm thông báo lỗi nếu cần

    return redirect('course:course_list')


def course_list(request):
    if request.user.is_superuser:
        # Superuser can see all courses
        courses = Course.objects.all()
    elif Course.objects.filter(instructor=request.user).exists():
        # Instructors can see all courses they are teaching, published or not
        courses = Course.objects.filter(
            Q(published=True) | Q(instructor=request.user)
        )
    else:
        courses = Course.objects.filter(published=True)  # Other users see only published courses

    module_groups = ModuleGroup.objects.all()
    enrollments = Enrollment.objects.filter(student=request.user)
    enrolled_courses = {enrollment.course.id for enrollment in enrollments}

    # Calculate completion percentage for each course
    for course in courses:
        course.completion_percent = course.get_completion_percent(request.user)

        # mới thêm
    recommended_courses = []
    for course in courses:
        if course.id not in enrolled_courses:
            for enrolled_course_id in enrolled_courses:
                enrolled_course = Course.objects.get(id=enrolled_course_id)
                enrolled_tags = set(enrolled_course.tags.split(',')) if enrolled_course.tags else set()
                current_tags = set(course.tags.split(',')) if course.tags else set()

                # Calculate the similarity
                if enrolled_tags:
                    shared_tags = enrolled_tags.intersection(current_tags)
                    similarity = len(shared_tags) / len(enrolled_tags)
                    if similarity >= 0.6:  # 60% similarity
                        recommended_courses.append(course)
                        break  # No need to check other enrolled courses

    # Pagination
    paginator = Paginator(courses, 10)  # Show 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'course_list.html', {
        'module_groups': module_groups,
        'page_obj': page_obj,  # Pagination object for template
        'courses': page_obj,  # Consistent with template expectations
        'enrolled_courses': enrolled_courses,  # To show enrolled status
        'recommended_courses': recommended_courses,
    })

def course_add(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)

        if course_form.is_valid():
            # Save the course
            course = course_form.save(commit=False)
            course.creator = request.user
            course.save()

            # Handle prerequisite courses (optional)
            prerequisite_ids = request.POST.getlist('prerequisite_courses[]')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_course = Course.objects.get(id=prerequisite_id)
                    course.prerequisites.add(prerequisite_course)

            # Create sessions for the course directly
            session_name = request.POST.get('session_name')
            session_quantity = int(request.POST.get('session_quantity', 0))
            if session_name and session_quantity > 0:
                for i in range(1, session_quantity + 1):
                    session = Session(
                        course=course,
                        name=f"{session_name}{i}",
                        order=i
                    )
                    session.save()

            messages.success(request, 'course and sessions created successfully.')
            return redirect('course:course_list')
        else:
            messages.error(request, 'There was an error creating the course. Please check the form.')

    else:
        course_form = CourseForm()
        session_form = SessionForm()

    all_courses = Course.objects.all()

    return render(request, 'course_form.html', {
        'course_form': course_form,
        'session_form': session_form,
        'all_courses': all_courses,
    })

# course/views.py
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    all_courses = Course.objects.exclude(id=course.id)

    if request.method == 'POST':
        course_form = CourseForm(request.POST, instance=course)

        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.creator = request.user

            # Handle tags
            tags = request.POST.get('tags', '').split(',')
            course.tags = ','.join(tag.strip() for tag in tags if tag.strip())  # Update tags

            # Save the course
            course.save()

            # Handle prerequisite deletion
            current_prerequisites = list(course.prerequisites.all())
            for prereq in current_prerequisites:
                if request.POST.get(f'delete_prerequisite_{prereq.id}'):
                    course.prerequisites.remove(prereq)

            # Handle adding new prerequisites
            prerequisite_ids = request.POST.getlist('prerequisite_courses')
            for prerequisite_id in prerequisite_ids:
                if prerequisite_id:
                    prerequisite_course = Course.objects.get(id=prerequisite_id)
                    course.prerequisites.add(prerequisite_course)

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
                    Session.objects.create(course=course, name=session_name, order=course.sessions.count() + 1)

            # Handle session deletion
            delete_session_ids = request.POST.getlist('delete_session_ids')
            for session_id in delete_session_ids:
                Session.objects.filter(id=session_id).delete()

            messages.success(request, 'course updated successfully.')
            return redirect('course:course_list')
        else:
            messages.error(request, 'There was an error updating the course. Please check the form.')

    else:
        course_form = CourseForm(instance=course)
        prerequisites = course.prerequisites.all()
        sessions = course.sessions.all()
        tags_list = course.tags.split(',') if course.tags else []

    return render(request, 'edit_form.html', {
        'course_form': course_form,
        'course': course,
        'prerequisites': prerequisites,
        'all_courses': all_courses,
        'sessions': sessions,  # Pass sessions to template
    })

def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course:course_list')
    return render(request, 'course_confirm_delete.html', {'course': course})

@login_required
def course_detail(request, pk):
    # Get the course based on the primary key (pk)
    course = get_object_or_404(Course, pk=pk)

    # Get related documents and videos
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    users_enrolled_count = Enrollment.objects.filter(course=course).count()

    # Get all feedback related to the course
    feedbacks = CourseFeedback.objects.filter(course=course)

    # Calculate the course's average rating
    if feedbacks.exists():
        total_rating = sum(feedback.average_rating() for feedback in feedbacks)
        course_average_rating = total_rating / feedbacks.count()
    else:
        course_average_rating = None  # No feedback yet

    # Get prerequisite courses directly from the course's `prerequisites` column
    prerequisites = course.prerequisites.all()

    sessions = Session.objects.filter(course=course)

    # Fetch the 5 newest feedback entries for this course
    latest_feedbacks = CourseFeedback.objects.filter(course=course).order_by('-created_at')[:5]

    context = {
        'course': course,
        'prerequisites': prerequisites,  # Pass prerequisites from the course model
        'is_enrolled': is_enrolled,
        'users_enrolled_count': users_enrolled_count,
        'course_average_rating': course_average_rating,
        'feedbacks': feedbacks,  # Pass feedbacks to the template
        'sessions': sessions,
        'latest_feedbacks': latest_feedbacks,
        'tags': course.tags.split(',') if course.tags else [],  # Pass tags as a list
    }

    return render(request, 'course_detail.html', context)

def users_enrolled(request, pk):
    # Lấy môn học dựa trên khóa chính (primary key)
    course = get_object_or_404(Course, pk=pk)

    # Lấy danh sách người dùng đã đăng ký môn học
    enrolled_users = Enrollment.objects.filter(course=course).select_related('student')

    return render(request, 'users_course_enrolled.html', {
        'course': course,
        'enrolled_users': enrolled_users,
    })

def course_search(request):
    form = CourseSearchForm(request.GET or None)
    query = request.GET.get('query', '')
    courses = Course.objects.all()

    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(course_code__icontains=query))

    # Add pagination for search results
    paginator = Paginator(courses, 10)  # Show 10 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,  # For paginated results
        'courses': page_obj,  # Pass the paginated courses as 'courses' for template consistency
    }
    return render(request, 'course_list.html', context)

@login_required
def reorder_course_materials(request, pk, session_id):
    # Fetch the course
    course = get_object_or_404(Course, pk=pk)

    # Fetch all sessions related to the course
    sessions = Session.objects.filter(course=course)

    # Fetch materials for the selected session, defaulting to the first session
    selected_session_id = request.POST.get('session_id') or session_id
    session = get_object_or_404(Session, id=selected_session_id)
    materials = ReadingMaterial.objects.filter(session=session).order_by('order')

    if request.method == 'POST':
        # Check if the request is for reordering materials
        if 'order' in request.POST:
            for material in materials:
                new_order = request.POST.get(f'order_{material.id}')
                if new_order:
                    material.order = int(new_order)  # Convert to integer
                    material.save()

            success_message = "Order updated successfully!"
            return render(request, 'reorder_course_material.html', {
                'course': course,
                'sessions': sessions,
                'materials': materials,
                'selected_session_id': selected_session_id,
                'success_message': success_message,
            })

    # Pass the course, sessions, and materials to the template
    return render(request, 'reorder_course_material.html', {
        'course': course,
        'sessions': sessions,
        'materials': materials,
        'selected_session_id': selected_session_id,
    })
def reading_material_detail(request, id):
    # Fetch the reading material by ID or return a 404 if it doesn't exist
    reading_material = get_object_or_404(ReadingMaterial, id=id)
    return render(request, 'reading_material_detail.html', {'reading_material': reading_material})

@login_required
def course_content(request, pk, session_id):
    course = get_object_or_404(Course, pk=pk)
    sessions = Session.objects.filter(course=course).order_by('order')

    selected_session_id = request.POST.get('session_id') or session_id

    current_session = get_object_or_404(Session, id=selected_session_id)

    materials = ReadingMaterial.objects.filter(session=current_session).order_by('order')

    file_id = request.GET.get('file_id')
    file_type = 'reading'
    current_material = None
    if file_id and file_type:
        try:
            current_material = ReadingMaterial.objects.get(id=file_id, material_type=file_type, session=current_session)
        except ReadingMaterial.DoesNotExist:
            current_material = materials.first() if materials.exists() else None
    else:
        current_material = materials.first() if materials.exists() else None

    next_material = materials.filter(order__gt=current_material.order).first() if current_material else None
    next_session = None

    if not next_material:
        next_session = Session.objects.filter(course=course, order__gt=current_session.order).order_by('order').first()
        if next_session:
            next_material = ReadingMaterial.objects.filter(session=next_session).order_by('order').first()

    content_type = None
    preview_content = None

    if current_material:
        if current_material.material_type == 'reading':
            reading = ReadingMaterial.objects.get(id=current_material.id)
            preview_content = reading.content
            content_type = 'reading'

    completion_status = Completion.objects.filter(
        session=current_session,
        material=current_material,
        user=request.user,
        completed=True
    ).exists() if current_material else False

    total_materials = ReadingMaterial.objects.filter(session__course=course).count()
    completed_materials = Completion.objects.filter(
        session__course=course,
        user=request.user,
        completed=True
    ).count()
    completion_percent = (completed_materials / total_materials) * 100 if total_materials > 0 else 0

    total_sessions = sessions.count()
    completed_sessions = SessionCompletion.objects.filter(course=course, user=request.user, completed=True).count()

    certificate_url = None
    if total_sessions > 0 and completed_sessions == total_sessions:
        # Call the function to generate the certificate URL
        certificate_url = reverse('course:generate_certificate', kwargs={'pk': course.pk})

    context = {
        'course': course,
        'sessions': sessions,
        'current_session': current_session,
        'materials': materials,
        'current_material': current_material,
        'next_material': next_material,
        'content_type': content_type,
        'preview_content': preview_content,
        'completion_status': completion_status,
        'completion_percent': completion_percent,
        'certificate_url': certificate_url,
        'next_session': next_session,
    }

    return render(request, 'course_content.html', context)


@require_POST
@login_required
def toggle_completion(request, pk):
    course = get_object_or_404(Course, pk=pk)
    file_id = request.POST.get('file_id')

    material = get_object_or_404(ReadingMaterial, id=file_id, session__course=course)
    session = material.session

    completion, created = Completion.objects.get_or_create(
        session=session,
        material=material,
        user=request.user,
    )
    completion.completed = not completion.completed
    completion.save()

    # Check if all materials in the session are completed
    total_materials = session.materials.count()
    completed_materials = Completion.objects.filter(session=session, user=request.user, completed=True).count()
    session_completed = total_materials == completed_materials

    SessionCompletion.objects.update_or_create(
        user=request.user,
        session=session,
        course=course,
        defaults={'completed': session_completed}
    )

    # Find the next item
    next_material = ReadingMaterial.objects.filter(
        session=session,
        order__gt=material.order
    ).order_by('order').first()

    next_session = None
    if not next_material:
        next_session = Session.objects.filter(course=course, order__gt=session.order).order_by('order').first()
        if next_session:
            next_material = ReadingMaterial.objects.filter(session=next_session).order_by('order').first()

    next_item_type = next_material.material_type if next_material else None
    next_item_id = next_material.id if next_material else None
    next_session_id = next_session.id if next_session else None

    return JsonResponse({
        'completed': completion.completed,
        'next_item_type': next_item_type,
        'next_item_id': next_item_id,
        'next_session_id': next_session_id
    })
# In course/views.py

@login_required
def course_content_edit(request, pk, session_id):
    order = 1
    course = get_object_or_404(Course, pk=pk)
    sessions = Session.objects.filter(course=course)

    # Default to the first session if not specified in POST
    selected_session_id = request.POST.get('session_id') or session_id
    session = get_object_or_404(Session, id=selected_session_id)

    # Fetch materials associated with the selected session
    materials = ReadingMaterial.objects.filter(session=session)
    #print("Materials associated with selected session:", [vars(material) for material in materials])  # List comprehension for material attributes

    reading_ids = materials.filter(material_type='reading').values_list('id', flat=True)

    reading_materials = ReadingMaterial.objects.filter(id__in=reading_ids)

    if request.method == 'POST':
        print("Session ID POST:", request.POST.get('session_id'))  # Debugging line

        # Process reading materials for deletion
        for reading_material in reading_materials:
            if f'delete_reading_material_{reading_material.id}' in request.POST:
                reading_material.delete()

        # Handle reading materials
        reading_material_titles = request.POST.getlist('reading_material_title[]')
        reading_material_contents = request.POST.getlist('reading_material_content[]')
        for title, content in zip(reading_material_titles, reading_material_contents):
            if title and content:
                reading_material = ReadingMaterial.objects.create(
                    session=session,
                    title=title,
                    content=content,
                    order=ReadingMaterial.objects.count() + 1
                )
                reading_material.save()

        messages.success(request, 'course content updated successfully.')
        return redirect(reverse('course:course_content_edit', args=[course.pk, session.id]))

    # Context to render the template
    context = {
        'course': course,
        'sessions': sessions,
        'selected_session': session,
        'reading_materials': reading_materials,
    }

    return render(request, 'course_content_edit.html', context)

@login_required
def toggle_publish(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user == course.instructor or request.user.is_superuser:
        course.published = not course.published
        course.save()
    return redirect('course:course_detail', pk=pk)

@login_required
def generate_certificate_png(request, pk):
    course = get_object_or_404(Course, pk=pk)
    student = request.user

    # Verify that the student has completed the course
    sessions = Session.objects.filter(course=course).count()
    completed_sessions = SessionCompletion.objects.filter(
        course=course,
        user=student,
        completed=True
    ).distinct().count()

    if completed_sessions != sessions:
        return HttpResponse("You have not completed this course yet.", status=403)

    # Dynamically find the background image in the course app's static directory
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Root of the project
    background_image_path = os.path.join(app_dir, 'course', 'static', 'course', 'images', 'certificate_background.jpg')

    if os.path.exists(background_image_path):
        with open(background_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
    else:
        return HttpResponse(f"Background image not found at {background_image_path}", status=500)

    # Generate the certificate
    context = {
        'student_name': student.get_full_name() or student.username,
        'course_name': course.name,
        'completion_date': datetime.now().strftime("%B %d, %Y"),
        'background_image_base64': encoded_string,
    }

    return render(request, 'certificate_template.html', context)
