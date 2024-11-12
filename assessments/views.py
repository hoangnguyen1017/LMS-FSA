from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from course.models import Course
from quiz.models import Question
from .models import Assessment,  StudentAssessmentAttempt, AnswerOption, UserAnswer, StudentAssessmentAttempt, InvitedCandidate
from .forms import AssessmentForm, AssessmentAttemptForm, InviteCandidatesForm
from exercises.models import Exercise
from quiz.models import Quiz
from django.db import IntegrityError, DatabaseError
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .tokens import invite_token_generator  # Adjust the import path as necessary
from django.utils.encoding import force_str
from django.db import transaction
from django.core.exceptions import ValidationError
from exercises.libs.submission import grade_submission, precheck
from exercises.models import Submission
from module_group.models import ModuleGroup
from django.db.models import Count
from django.http import Http404
#Working

from django.utils.http import urlencode
from django.core.validators import validate_email

def pre_take_ass(request, assessment):
    print("bắt đầu thực hiện pretake_âss")
    if not request.user.is_authenticated and request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        
        print(f"POST request received: email={email}, name={name}")  # This should print if the form is submitted

        if not email or not name:
            print("Error: Missing name or email.")
            return render(request, 'assessment/take_assessment.html', {
                'assessment': assessment,
                # 'questions': questions,
                # 'exercises': exercises,
                'error': 'Both Name and Email are required for taking this assessment.',
            })

# will delete
@login_required
def invite_candidates_add_attemp(request, pk):
    print("bắt đầu thực hiện invite_candidates_add_attemp")
    assessment = get_object_or_404(Assessment, pk=pk)

    if request.method == 'POST':
        form = InviteCandidatesForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['emails'].split(',')
            emails = [email.strip() for email in emails if email.strip()]

            invited_candidates = []

            for email in emails:
                # Check if the email has already been invited
                if not InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                    # Create an InvitedCandidate instance
                    invited_candidate = InvitedCandidate.objects.create(
                        assessment=assessment,
                        email=email
                    )
                    invited_candidate.set_expiration_date(days=7)
                    invited_candidate.save()

                    # Create a StudentAssessmentAttempt immediately for the invited candidate
                    attempt = StudentAssessmentAttempt.objects.create(
                        user=None,  # User is None since they aren't authenticated yet
                        email=email,
                        assessment=assessment,
                        score_quiz=0.0,
                        score_ass=0.0
                    )

                    # Generate the invitation link
                    token = invite_token_generator.make_token(invited_candidate)
                    uid = urlsafe_base64_encode(force_bytes(invited_candidate.pk))
                    invite_link = request.build_absolute_uri(
                        reverse('assessment:assessment_invite_accept', kwargs={'uidb64': uid, 'token': token})
                    )
                    
                    # Send the invite email with the token link
                    send_mail(
                        subject=f"You're invited to complete an assessment: {assessment.title}",
                        message=f"Please click the link below to access the assessment. This link will expire in 7 days.\n\n{invite_link}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                    )

                    # Track the invited candidate
                    invited_candidates.append(invited_candidate)

            # Update the invited count for the assessment
            assessment.invited_count += len(invited_candidates)
            assessment.save()

            return redirect('assessment:assessment_list')

    else:
        form = InviteCandidatesForm()

    return render(request, 'assessment/invite_candidates.html', {
        'form': form,
        'assessment': assessment,
    })

# will delete it
def take_assessment_add_attemp(request, assessment_id):
    print("bắt đầu thực hiện take_assessment_add_attemp")
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.questions.all()
    exercises = assessment.exercises.all()
    total_marks = assessment.total_score
    total_questions = questions.count()

    # Check if the user is in preview mode
    is_preview = request.GET.get('preview', 'false').lower() == 'true'
    
    if is_preview:
        return render(request, 'assessment/take_assessment.html', {
            'assessment': assessment,
            'questions': questions,
            'exercises': exercises,
            'is_preview': True,
        })

    attempt_id = request.session.get('attempt_id')
    email = None

    # If the user is unauthenticated, check for an attempt created from invitation
    if not request.user.is_authenticated:
        email = request.GET.get('email')  # Retrieve email from query parameters
        if email:
            # Try to retrieve the existing attempt based on the email and assessment
            attempt = StudentAssessmentAttempt.objects.filter(email=email, assessment=assessment).first()
            if attempt:
                # Set session attempt ID for easy access in further requests
                request.session['attempt_id'] = attempt.id
                attempt_id = attempt.id
                print(f"Using existing attempt with ID: {attempt.id} for email: {email}")
            else:
                print("No existing attempt found for email:", email)

    # Handle form submissions if attempt exists
    if request.method == 'POST' and attempt_id:
        attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id)

        print(f"Attempt found with ID: {attempt.id}. Processing answers.")

        correct_answers = 0

        # Process questions
        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            selected_option = None

            if selected_option_id and selected_option_id.isdigit():
                selected_option = AnswerOption.objects.get(id=int(selected_option_id))

            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
            )

            if selected_option and selected_option.is_correct:
                correct_answers += 1

        # Process exercises if needed
        total_exercise_score = 0
        for exercise in exercises:
            submissions = Submission.objects.filter(exercise=exercise, assessment=assessment)
            exercise_score = sum(submission.score for submission in submissions if submission.score is not None)
            total_exercise_score += exercise_score

        attempt.score_quiz = (total_marks / total_questions) * correct_answers
        attempt.score_ass = total_exercise_score
        attempt.save()

        print(f"Assessment completed. Redirecting to results.")
        return redirect('assessment:assessment_result', assessment_id=assessment.id, attempt_id=attempt.id)

    # Render the assessment page if no POST submission is made
    print('Rendering assessment page.')
    return render(request, 'assessment/take_assessment.html', {
        'assessment': assessment,
        'questions': questions,
        'exercises': exercises,
        'is_preview': False,
        'anonymous': not request.user.is_authenticated,
        'email': email,
    })


def invite_candidates(request, pk):
    print("bắt đầu thực hiện invite_candidates")
    assessment = get_object_or_404(Assessment, pk=pk)

    if request.method == 'POST':
        form = InviteCandidatesForm(request.POST)
        print(f"form trong invite candidate la: {form}")
        if form.is_valid():
            emails = form.cleaned_data['emails'].split(',')
            emails = [email.strip() for email in emails if email.strip()]
            print(f"email sau khi clean là {emails}")

            # Track invited candidates to avoid duplicates
            invited_candidates = []

            for email in emails:
                # Check if the email is already invited
                if not InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                #if InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                    invited_candidate = InvitedCandidate.objects.create(
                        assessment=assessment,
                        email=email
                    )
                    print(f"invite candidate sau khi được tạo")
                    invited_candidate.set_expiration_date(days=7)  # Set expiration to 7 days

                    invited_candidate.save()

                    # Generate a token with an expiration time
                    token = invite_token_generator.make_token(invited_candidate)
                    print(f"token àter invite{token}")
                    uid = urlsafe_base64_encode(force_bytes(invited_candidate.pk))
                    print(f"uid là {uid}")

                    # Create the invite URL with the token
                    invite_link = request.build_absolute_uri(
                        reverse('assessment:assessment_invite_accept', kwargs={'uidb64': uid, 'token': token})
                    )
                    print(f"invite link là {invite_link}")

                    # Send the invite email with the token link
                    send_mail(
                        subject=f"You're invited to complete an assessment: {assessment.title}",
                        message=f"Please click the link below to access the assessment. This link will expire in 7 days.\n\n{invite_link}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                    )

                    # Track the invited candidate
                    invited_candidates.append(invited_candidate)

            # Update invited_count based on the number of unique invited candidates
            assessment.invited_count += len(invited_candidates)
            assessment.save()

            return redirect('assessment:assessment_list')

    else:
        form = InviteCandidatesForm()

    return render(request, 'assessment/invite_candidates.html', {
        'form': form,
        'assessment': assessment,
    })

def take_assessment(request, assessment_id):
    print("bắt đầu thực hiện take_assessment")
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.questions.all()
    exercises = assessment.exercises.all()
    total_marks = assessment.total_score
    total_questions = questions.count()

    # Check if the user is in preview mode
    is_preview = request.GET.get('preview', 'false').lower() == 'true'
    if is_preview:
        return render(request, 'assessment/take_assessment.html', {
            'assessment': assessment,
            'questions': questions,
            'exercises': exercises,
            'is_preview': True,
        })

    # Retrieve attempt ID from session
    attempt_id = request.session.get('attempt_id')              #  assessment_detail
    email = request.GET.get('email') if not request.user.is_authenticated else None

    # Handle unauthenticated users with email verification
    if not request.user.is_authenticated and email:
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'assessment/take_assessment.html', {
                'assessment': assessment,
                'questions': questions,
                'exercises': exercises,
                'error': 'Please provide a valid email address.',
                'email': email
            })

    if request.method == 'POST':
        email = request.POST.get('email')  # Get the email from the form data
        # Start a new attempt if it doesn't exist in the session
        if attempt_id:
            attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id)
            print(f"ateempt là {attempt}")
        else:
            # Create a new attempt in an atomic transaction
            with transaction.atomic():
                attempt = StudentAssessmentAttempt.objects.create(
                    user=request.user.id if request.user.is_authenticated else None,
                    email=email,
                    assessment=assessment,
                    score_quiz=0.0,
                    score_ass=0.0
                )

                request.session['attempt_id'] = attempt.id  # Save attempt ID to session

        correct_answers = 0

        # Process each question
        for question in questions:
            # Fetch all selected option IDs for the question (adjust if using checkboxes or other multi-select elements)
            selected_option_ids = request.POST.getlist(f'question_{question.id}')
            text_response = request.POST.get(f'text_response_{question.id}')

            # Initialize selected_options as an empty list to store AnswerOption instances
            selected_options = []

            # Populate selected_options with AnswerOption instances if IDs are valid
            if selected_option_ids:
                selected_options = AnswerOption.objects.filter(id__in=selected_option_ids)

            # Create a UserAnswer instance for the question, excluding selected_options for now
            student_answer = UserAnswer.objects.create(
                assessment=assessment,
                question=question,
                text_response=text_response  # Keep text_response field
            )

            # Set the selected options using the ManyToManyField's set method
            student_answer.selected_options.set(selected_options)

            # Optional: Count correct answers if selected options are supposed to be evaluated for correctness
            correct_answers += sum(1 for option in selected_options if option.is_correct)

        total_quiz_score = (total_marks / total_questions) * correct_answers

        # Calculate and save exercise scores
        total_exercise_score = sum(
            submission.score for exercise in exercises
            for submission in Submission.objects.filter(exercise=exercise, assessment=assessment)
            if submission.score is not None
        )

        try:
            attempt.score_quiz = total_quiz_score
            attempt.score_ass = total_exercise_score
            attempt.save()
            attempt_id = attempt.id
        except IntegrityError as e:
            # Xử lý khi có lỗi vi phạm ràng buộc dữ liệu
            print(f"Lỗi IntegrityError: {e}")
        except DatabaseError as e:
            # Xử lý các lỗi liên quan đến cơ sở dữ liệu khác
            print(f"Lỗi DatabaseError: {e}")
        except Exception as e:
            # Xử lý các ngoại lệ khác
            print(f"Một lỗi không mong muốn đã xảy ra: {e}")  # Store the attempt_id after saving the attempt
        # Redirect to the results page with attempt details
        if email:  # Check if email is provided
            return redirect(
                'assessment:assessment_result',  # Use the name for the URL with email
                assessment_id=assessment.id,
                attempt_id=attempt.id,  # Ensure this is the correct attempt ID
                email=email  # Include email if available
            )
        else:
            return redirect(
                'assessment:assessment_result_no_email',  # Use the name for the URL without email
                assessment_id=assessment.id,
                attempt_id=attempt.id  # Redirect without email if not available
            )


    # Render the assessment page
    return render(request, 'assessment/take_assessment.html', {
        'assessment': assessment,
        'questions': questions,
        'exercises': exercises,
        'is_preview': False,
        'anonymous': not request.user.is_authenticated,
        'email': email,
        'attempt_id': attempt_id  # This will be None for GET request
    })
#---
def assessment_report(request , assessment_id , attempt_id , email=None):
    print("bắt đầu thực hiện assessment_report")
    assessment=get_object_or_404(Assessment, id=assessment_id)
    print(f"assessment làaaa: {assessment}")
    user_answers = UserAnswer.objects.filter(assessment=assessment)
    print(f"email là : {email}")
    print(f"assessment_id là : {assessment_id}")
    print(f"user_answers làaaa: {user_answers}")
    print(f"attempt_id làaaa: {attempt_id}")
    print(f"request.user là :{request.user}")
    print(f"request.user.is_authenticated là :{request.user.is_authenticated}")
    try:
        if request.user.is_authenticated:
            attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, assessment_id=assessment)
            print(f"Attempt with if :{attempt}")
        if request.user.is_authenticated and email:
            attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, email=email, assessment_id=assessment)
            print(f"attempt with email :{attempt}")
        else:
            raise Http404("No email provided for anonymous user.")  # Or redirect to an error page
            print("loi rồi ne")
        # Access the StudentAssessmentAttempt directly since Submission.attempt is defined.
        user_submissions = Submission.objects.filter(exercise__assessments=assessment, user__email=email)
        print(f"user_submission lafff : {user_submissions}")   

        # Calculate the total score (already stored in the attempt object)
        score_ass = attempt.score_ass
        score_quiz = attempt.score_quiz

        context = {
            'assessment': assessment,
            'attempt': attempt,
            'user_answers': user_answers,
            'user_submissions': user_submissions,
            'score_ass': score_ass,
            'score_quiz': score_quiz,
        }

        # Render the result page
        return render(request, 'assessment/assessment_report.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")
        return render(request, 'assessment/error.html', {'error': 'Attempt not found. Please ensure you have provided a valid email.'})

def assessment_result(request, assessment_id, attempt_id, email=None):
    print("bắt đầu thực hiện assessment_result")
    # Get the assessment object and the user's attempt
    assessment = get_object_or_404(Assessment, id=assessment_id)
    # Get all user answers for this attempt
    user_answers = UserAnswer.objects.filter(assessment=assessment)

    # Retrieve the user's attempt
    if request.user.is_authenticated:
        # If the user is authenticated, retrieve by user
        attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, user=request.user)
        user_submissions = Submission.objects.filter(exercise__assessments=assessment, user=request.user)
    else:
        # If the user is anonymous, check if email is provided
        if email:
            attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, email=email)
            user_submissions = Submission.objects.filter(exercise__assessments=assessment, user__email=email)
        else:
            # Handle the case where email is None
            return render(request, 'assessment/error.html', {
                'error': 'Attempt not found. Please ensure you have provided a valid email.'
            })
        
    # Assuming 'email' variable is already defined and contains the user's email when not authenticated
    if request.user.is_authenticated:
        attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, user=request.user)
        user_submissions = Submission.objects.filter(exercise__assessments=assessment, user=request.user)
    else:
        attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id, email=email)
        user_submissions = Submission.objects.filter(exercise__assessments=assessment, user__email=email)
        

    # Calculate the total score (already stored in the attempt object)
    score_ass = attempt.score_ass
    score_quiz = attempt.score_quiz

    context = {
        'assessment': assessment,
        'attempt': attempt,
        'user_answers': user_answers,
        'user_submissions': user_submissions,
        'score_ass': score_ass,
        'score_quiz': score_quiz,
    }

    # Render the result page
    return render(request, 'assessment/assessment_result.html', context)


from django.shortcuts import redirect

def handle_anonymous_info(request, invited_candidate_id):
    print("bắt đầu thực hiện handle_anonymous_info")
    
    invited_candidate = InvitedCandidate.objects.get(pk=invited_candidate_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Validate and create a StudentAssessmentAttempt or whatever logic you need
        # e.g., create or update the User, create a session, etc.

        # Assuming successful processing, redirect to assessment
        # Create query parameters for redirect
        query_params = urlencode({'email': email})
        print(f"handle anonymouse_info là {query_params}")

        # if name and email:
        #     # Lưu thông tin name vào session
        #     request.session['name'] = name
        #     print(f"Tên đã được lưu vào session: {name}")

        #     # Redirect tới assessment detail
        #     return redirect('assessment:assessment_detail', pk=invited_candidate.assessment.id)
             
        # Redirect to take_assessment with email as a query parameter
        return redirect(f"{reverse('assessment:take_assessment', kwargs={'assessment_id': invited_candidate.assessment.id})}?{query_params}")
        # return redirect('assessment:take_assessment', assessment_id=invited_candidate.assessment.id)
    else:
        # Handle the case where this view is accessed without POST (should not happen)
        messages.error(request, "Invalid request.")
        return redirect('assessment:assessment_list')


def assessment_invite_accept(request, uidb64, token):       #sau khi invite candidate thì sẽ đưa vô hàm accept
    print("bắt đầu thực hiện assessment_invite_accept")
    try:
        # Decode the uidb64 to get the InvitedCandidate ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"sau khi invite_accept thì uid đươcj mã hóa là uid")
        invited_candidate = InvitedCandidate.objects.get(pk=uid)
        print(f"invite candidate sau khi được accept là obj : {invited_candidate}")
        # Check if the token is valid
        if invite_token_generator.check_token(invited_candidate, token):
            # Check if the invitation is expired
            if invited_candidate.expiration_date >= timezone.now():
                # Invitation is valid
                assessment = invited_candidate.assessment
                
                
                # If user is authenticated, render the assessment directly
                if request.user.is_authenticated:
                    print(f"assessment_invite_accept : người dùng được authenticated và chuyển hướng sang take_ass")
                    return render(request, 'assessment/take_assessment.html', {
                        'assessment': assessment,
                    })
                else:
                    # If user is not authenticated, render the information collection form
                    print(f"assessment_invite_accept : người dùng không được authenticated và chuyển hướng sang anonymous input")
                    return render(request, 'assessment/anonymous_input.html', {
                        'assessment': assessment,
                        'invited_candidate_id': invited_candidate.id
                    })


            else:
                messages.error(request, "This invitation link has expired.")
                return redirect('assessment:assessment_list')  # Redirect as appropriate

        else:
            print("link bị invalid")
            messages.error(request, "This invitation link is invalid.")
            return redirect('assessment:assessment_list')  # Redirect as appropriate

    except (TypeError, ValueError, OverflowError, InvitedCandidate.DoesNotExist):
        messages.error(request, "This invitation link is invalid.")
        return redirect('assessment:assessment_list')  # Redirect as appropriate


@login_required
# def assessment_detail(request, pk):
#     assessment = get_object_or_404(Assessment, pk=pk)
    
#     # Query invited candidates for this assessment
#     invited_candidates = InvitedCandidate.objects.filter(assessment=assessment)
   
#     # Query attempts from registered users
#     registered_attempts = StudentAssessmentAttempt.objects.filter(assessment=assessment)
    
#     # Query attempts from non-registered candidates
#     # non_registered_attempts = NonRegisteredCandidateAttempt.objects.filter(assessment=assessment)

#     return render(request, 'assessment/assessment_detail.html', {
#         'assessment': assessment,
#         'invited_candidates': invited_candidates,
#         'registered_attempts': registered_attempts,
#         # 'non_registered_attempts': non_registered_attempts,
#     })


def assessment_detail(request, pk):    
    print("bắt đầu thực hiện assessment_detail")
                     # def take_assessment
    assessment = get_object_or_404(Assessment, pk=pk)
    print(assessment)
    # print(attempt_id)
    # if attempt_id:
    #         attempt = get_object_or_404(StudentAssessmentAttempt, id=attempt_id)
    
    # Query invited candidates for this assessment
    invited_candidates = InvitedCandidate.objects.filter(assessment=assessment)
    # invited_candidates = sorted(invited_candidates, key=lambda x: x.score_quiz, reverse=True)
    # Query attempts from registered users
    registered_attempts = StudentAssessmentAttempt.objects.filter(assessment=assessment).order_by('attempt_date')
    
    print(f"registered_attempts trong detail là : {registered_attempts} ")
    
    # name=request.session.get('name')
    # print(f"name là {name}")
    # Query for all user answers
    user_answers = UserAnswer.objects.filter(assessment=assessment)
    
    # Query for all exercise submissions
    user_submissions = Submission.objects.filter(exercise__assessments=assessment)
    count = 0
    name_of_student=''
    
    return render(request, 'assessment/assessment_detail.html', {
        'assessment': assessment,
        'invited_candidates': invited_candidates,
        'registered_attempts': registered_attempts,
        'user_answers': user_answers,
        'user_submissions': user_submissions,
        'count': count,
        # 'name':name
        
        
    })

@login_required
def assessment_create(request):
    print("bắt đầu thực hiện assessment_create")
    query = request.GET.get('search', '')
    exercises = Exercise.objects.filter(title__icontains=query)  # Filter exercises based on search query
    questions = Question.objects.filter(question_text__icontains=query)  # Filter questions based on search query
  
    paginator = Paginator(exercises, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        selected_exercises = request.POST.getlist('exercises')  # Get selected exercises from form
        selected_questions = request.POST.getlist('questions')  # Get selected questions from the form

        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            form.save_m2m()  # Save ManyToMany relationships

            # Add selected exercises to the assessment
            for exercise_id in selected_exercises:
                exercise = get_object_or_404(Exercise, id=exercise_id)
                assessment.exercises.add(exercise)  # Add the exercises to assessment

            # Add selected questions to the assessment
            for question_id in selected_questions:
                question = get_object_or_404(Question, id=question_id)
                assessment.questions.add(question)  # Add questions to the assessment

            messages.success(request, 'Assessment created successfully with exercises!')
            return redirect('assessment:assessment_list')

    else:
        form = AssessmentForm()

    return render(request, 'assessment/assessment_create.html', {
        'form': form,
        'exercises': exercises,
        'questions': questions,
        'page_obj': page_obj,
        'selected_exercises': [],  # Initially no exercises selected
        'selected_questions': [],  # Initially no questions selected
        'search': query
    })


@login_required
def assessment_edit(request, pk):
    print("bắt đầu thực hiện assessment_edit")
    assessment = get_object_or_404(Assessment, id=pk)
    form = AssessmentForm(instance=assessment)

    # Fetch all available exercises and questions
    exercises = Exercise.objects.all()
    selected_exercises = assessment.exercises.values_list('id', flat=True)


    # Fetch quizzes
    all_quizzes = Quiz.objects.annotate(total_questions=Count('questions'))
    quiz_questions = []
    total_questions_selected_quiz = 0
    selected_quiz = None

    # Check if another quiz is selected to pull questions from
    selected_quiz_id = request.GET.get('selected_quiz')
    if selected_quiz_id:
        selected_quiz = get_object_or_404(Quiz, id=selected_quiz_id)
        questions = selected_quiz.questions.prefetch_related('answer_options')

        for question in questions:
            answers = question.answer_options.all()
            quiz_questions.append({
                'id': question.id,
                'text': question.question_text,
                'answers': [{'id': answer.id, 'text': answer.option_text, 'is_correct': answer.is_correct} for answer in answers]
            })
        total_questions_selected_quiz = questions.count()

    if request.method == "POST":
        form = AssessmentForm(request.POST, instance=assessment)

        if form.is_valid():
            assessment = form.save()

            # Update associated exercises
            selected_exercise_ids = request.POST.getlist('exercises')
            assessment.exercises.set(selected_exercise_ids)
            
            selected_question_ids = request.POST.getlist('selected_questions[]') #Corrected name
            if selected_question_ids:
                assessment.questions.set(selected_question_ids) # Efficient way to associate
                
                assessment.save()

            messages.success(request, 'The assessment has been successfully saved.')
            return redirect('assessment:assessment_list')

        # Process questions and answers updates
        data = json.loads(request.body) if request.body else {}
        received_questions = data.get('questions', [])

        for item in received_questions:
            question_id = item.get('id')
            question_text = item.get('text')
            answers = item.get('answers', [])
            received_answer_ids = {answer.get('id') for answer in answers if 'id' in answer}

            if question_id:
                try:
                    question = Question.objects.get(id=question_id)
                    question.question_text = question_text
                    question.save()

                    # Delete answers not present in received answers
                    existing_answer_ids = set(question.answer_options.values_list('id', flat=True))
                    answers_to_delete = existing_answer_ids - received_answer_ids
                    AnswerOption.objects.filter(id__in=answers_to_delete).delete()

                except Question.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Question with ID {question_id} not found.'}, status=400)
            else:
                question = Question.objects.create(quiz=selected_quiz, question_text=question_text)

            for answer_data in answers:
                answer_id = answer_data.get('id')
                answer_text = answer_data.get('text')
                is_correct = answer_data.get('is_correct', True)

                if answer_id:
                    try:
                        answer = AnswerOption.objects.get(id=answer_id)
                        answer.option_text = answer_text
                        answer.is_correct = is_correct
                        answer.save()
                    except AnswerOption.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Answer with ID {answer_id} not found.'}, status=400)
                else:
                    AnswerOption.objects.create(question=question, option_text=answer_text, is_correct=is_correct)

        return JsonResponse({'status': 'success', 'message': 'Questions updated successfully.'})

    # Render the combined context with both form and fetched data
    context = {
        'form': form,
        'assessment': assessment,
        'exercises': exercises,
        'selected_exercises': selected_exercises,
        
        'all_quizzes': all_quizzes,
        'selected_quiz': selected_quiz,
        'quiz_questions': quiz_questions,
        'total_questions_selected_quiz': total_questions_selected_quiz,
    }

    return render(request, 'assessment/assessment_form.html', context)

@login_required
def assessment_list(request):
    print("bắt đầu thực hiện assessment_list")
    #quizzes = Quiz.objects.select_related('course').annotate(question_count=Count('questions')).all().order_by('-created_at')
    courses = Course.objects.all().order_by('course_name')
    assessments = Assessment.objects.all().order_by('created_at')

    # Lọc quiz dựa trên subject được chọn
    selected_course = request.GET.get('course', '')
    
    if selected_course:
        assessments = assessments.filter(course__id=selected_course)
  
    
    # Dynamically calculate exercise and question counts for each assessment
    assessments_with_counts = []
    for assessment in assessments:
        # Assuming you have related models for exercises and questions
        exercise_count = assessment.exercises.count()  # Assuming 'exercises' is a related field
        question_count = assessment.questions.count()  # Assuming 'questions' is a related field in exercises
        assessments_with_counts.append({
            'selected_course': selected_course,
            'assessment': assessment,
            'exercise_count': exercise_count,
            'question_count': question_count,
        })

    module_groups = ModuleGroup.objects.all()
    # Pass the assessments with their exercise and question counts to the template
    return render(request, 'assessment/assessment_list.html', {
        'module_groups': module_groups,
        'courses': courses,
        'assessments_with_counts': assessments_with_counts,
    })


@login_required
def get_exercise_content(request, exercise_id):
    print("bắt đầu thực hiện get_exercise_content")
    exercise = Exercise.objects.get(id=exercise_id)
    return JsonResponse({
        'title': exercise.title,
        'content': exercise.description  
    })


@login_required
def student_assessment_attempt(request, assessment_id):
    print("bắt đầu thực hiện student_assessment_attempt")
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == 'POST':
        form = AssessmentAttemptForm(request.POST)
        if form.is_valid():
            attempt = form.save(commit=False)
            attempt.user = request.user
            attempt.assessment = assessment
            attempt.save()
            messages.success(request, 'Your attempt has been recorded.')
            return redirect('assessment:assessment_detail', pk=assessment.id)
    else:
        form = AssessmentAttemptForm()
    return render(request, 'assessment/assessment_attempt_form.html', {'form': form, 'assessment': assessment})
