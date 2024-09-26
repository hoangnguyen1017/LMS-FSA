from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
import json
from .models import Quiz, Submission, SubmittedAnswer
from .forms import QuizForm, SubmissionForm, GradingForm
from question.models import Question, Answer
from module_group.models import Module, ModuleGroup  # Import the existing ModuleGroup model
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from random import shuffle, sample
import random

def check_quiz_due_date(view_func):
    def wrapper(request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if quiz.is_past_due():
            messages.error(request, "This quiz is past its due date and is no longer accessible.")
            return redirect('quiz:quiz_list')
        return view_func(request, quiz_id, *args, **kwargs)
    return wrapper

@login_required
def quiz_list(request):
    all_quizzes = Quiz.objects.all().order_by('-created_at')
    module_groups = ModuleGroup.objects.all()

    for quiz in all_quizzes:
        quiz.user_submissions = Submission.objects.filter(quiz=quiz, student=request.user)
        quiz.is_past_due = quiz.is_past_due()
        quiz.attempts_left = quiz.attempts_left(request.user)
        quiz.calculated_grade = quiz.calculate_grade(request.user)

    context = {
        'quizzes': all_quizzes,
        'module_groups': module_groups
    }
    return render(request, 'quiz_list.html', context)

@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()

            subject = form.cleaned_data['subject']
            category = form.cleaned_data['category']
            num_questions = request.POST.get('num_questions')

            if num_questions:
                # Randomly select questions
                available_questions = Question.objects.filter(subject=subject, category=category)
                num_questions = min(int(num_questions), available_questions.count())
                selected_questions = random.sample(list(available_questions), num_questions)
            else:
                # Manually selected questions
                selected_questions = request.POST.getlist('selected_questions')

            quiz.questions.set(selected_questions)
            messages.success(request, 'Quiz created successfully.')
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm()

    return render(request, 'create_quiz.html', {'form': form})

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save()
            selected_questions = request.POST.getlist('selected_questions')
            quiz.questions.set(selected_questions)
            messages.success(request, 'Quiz updated successfully.')
            return redirect('quiz:quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'edit_quiz.html', {'form': form, 'quiz': quiz})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        return redirect('quiz:quiz_list')
    return render(request, 'delete_quiz.html', {'quiz': quiz})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    is_past_due = quiz.is_past_due()
    user_submissions = Submission.objects.filter(quiz=quiz, student=request.user)
    attempts_left = quiz.attempts_left(request.user)
    calculated_grade = quiz.calculate_grade(request.user)

    context = {
        'quiz': quiz,
        'is_past_due': is_past_due,
        'user_submissions': user_submissions,
        'attempts_left': attempts_left,
        'calculated_grade': calculated_grade,
    }
    return render(request, 'quiz_detail.html', context)

@login_required
@check_quiz_due_date
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not quiz.is_open_for_submission():
        messages.error(request, "This quiz is not open for submission.")
        return redirect('quiz:quiz_list')

    if quiz.attempts_left(request.user) <= 0:
        messages.error(request, "You have used all your attempts for this quiz.")
        return redirect('quiz:quiz_detail', quiz_id=quiz.id)

    questions = list(quiz.questions.all())
    shuffle(questions)  # Shuffle the questions

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.quiz = quiz
            submission.student = request.user
            try:
                submission.save()
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('quiz:quiz_list')

            for question in questions:
                answer_text = request.POST.get(f'answer_{question.id}')
                if answer_text:
                    SubmittedAnswer.objects.create(
                        submission=submission,
                        question=question,
                        text=answer_text
                    )

            submission.grade = submission.calculate_score()
            submission.save()
            return redirect('quiz:submission_result', submission_id=submission.id)
    else:
        form = SubmissionForm()

    return render(request, 'submit_quiz.html', {'quiz': quiz, 'form': form, 'questions': questions})

@login_required
def submission_result(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    submitted_answers = submission.submitted_answers.all().select_related('question')

    result_data = []
    for submitted_answer in submitted_answers:
        question = submitted_answer.question
        correct_answer = question.answers.filter(is_correct=True).first()
        result_data.append({
            'question': question.question_text,
            'user_answer': submitted_answer.text,
            'correct_answer': correct_answer.text if correct_answer else 'N/A',
            'is_correct': submitted_answer.text == correct_answer.text if correct_answer else False
        })

    context = {
        'submission': submission,
        'result_data': result_data,
        'grade': submission.grade
    }
    return render(request, 'submission_result.html', context)

@login_required
def make_question(request):
    subject = request.GET.get('subject')
    category = request.GET.get('category')

    questions = Question.objects.filter(
        Q(subject__id=subject) & Q(category__id=category)
    )

    return render(request, 'make_question.html', {'questions': questions})

@login_required
def load_questions(request):
    subject_id = request.GET.get('subject')
    category_id = request.GET.get('category')

    questions = Question.objects.filter(
        id=subject_id,
        category_id=category_id
    )

    questions_data = []
    for question in questions:
        question_data = {
            'id': question.id,
            'text': str(question),  # Using __str__ method of the Question model
            'answers': [
                {
                    'id': answer.id,
                    'text': str(answer),  # Using __str__ method of the Answer model
                    'is_correct': answer.is_correct if hasattr(answer, 'is_correct') else False
                } for answer in question.answers.all()
            ]
        }
        questions_data.append(question_data)

    return JsonResponse({'questions': questions_data})

