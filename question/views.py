from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from module_group.models import ModuleGroup
from django.urls import reverse
# Question views
def question_list(request):
    module_groups = ModuleGroup.objects.all()
    questions = Question.objects.all()
    return render(request, 'question_list.html', {'questions': questions, 'module_groups':module_groups})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'question_detail.html', {'question': question})


def question_add(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()
            print(request.POST.getlist('answer_text[]'))
            print(request.POST.getlist('is_correct[]'))

            # Process answer formset data
            answer_texts = request.POST.getlist('answer_text[]')
            is_correct_list = request.POST.getlist('is_correct[]')

            # Create a dictionary of answer indices and their correctness
            is_correct_dict = {i: (i < len(is_correct_list) and is_correct_list[i] == 'True') for i in
                               range(len(answer_texts))}

            for i, answer_text in enumerate(answer_texts):
                is_correct = is_correct_dict.get(i, False)  # Defaults to False if not found
                Answer.objects.create(question=question, text=answer_text, is_correct=is_correct)

            # Redirect to question list page after successful save
            return redirect('question:question_list')
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
