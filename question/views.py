from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from module_group.models import ModuleGroup
from django.urls import reverse
from subject.models import Subject
from category.models import Category, SubCategory
from django.contrib import messages


# Question views
def question_list(request):
    subjects = Subject.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    questions = Question.objects.all()

    # Filter by subject
    subject_id = request.GET.get('subject')
    if subject_id:
        questions = questions.filter(subject_id=subject_id)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        questions = questions.filter(category_id=category_id)

    # Filter by subcategory
    subcategory_id = request.GET.get('subcategory')
    if subcategory_id:
        questions = questions.filter(subcategory_id=subcategory_id)  # Changed this line

    # Filter by method of answer
    method = request.GET.get('method')
    if method:
        if method == 'essay':
            questions = questions.filter(answers__isnull=True)
        elif method == 'multiple_choice':
            questions = questions.filter(answers__isnull=False).distinct()

    context = {
        'questions': questions,
        'subjects': subjects,
        'categories': categories,
        'subcategories': subcategories,
        'selected_subject': subject_id,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'selected_method': method,
    }

    return render(request, 'question_list.html', context)


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'question_detail.html', {'question': question})


def question_add(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()

            # Process answer formset data
            answer_texts = request.POST.getlist('answer_text[]')
            is_correct_list = request.POST.getlist('is_correct[]')

            # Create a dictionary of answer indices and their correctness
            is_correct_dict = {i: (i < len(is_correct_list) and is_correct_list[i] == 'True') for i in
                               range(len(answer_texts))}

            for i, answer_text in enumerate(answer_texts):
                if answer_text.strip():  # Only create answer if text is not empty
                    is_correct = is_correct_dict.get(i, False)  # Defaults to False if not found
                    Answer.objects.create(question=question, text=answer_text, is_correct=is_correct)

            messages.success(request, 'Question added successfully!')
            return redirect('question:question_list')
        else:
            messages.error(request, 'There was an error adding the question. Please check the form.')
    else:
        question_form = QuestionForm()

    return render(request, 'question_add.html', {'question_form': question_form})


def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question:question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'question_form.html', {'form': form})


def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('question:question_list')
    return render(request, 'question_confirm_delete.html', {'question': question})


def answer_add(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('question:question_detail', pk=question.pk)
    else:
        form = AnswerForm()
    return render(request, 'answer_form.html', {'form': form, 'question': question})


def question_filter(request):
    module_groups = ModuleGroup.objects.all()
    subjects = Subject.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()  # Add this line

    context = {
        'module_groups': module_groups,
        'subjects': subjects,
        'categories': categories,
        'subcategories': subcategories,  # Add this line
    }

    return render(request, 'question_filter.html', context)