from django.shortcuts import render, redirect, get_object_or_404
from .models import QuizQuestionAnswer, UserAnswer
from .forms import QuizQuestionAnswerForm, UserAnswerForm

# Hiển thị danh sách câu hỏi và câu trả lời
def quiz_home(request):
    questions = QuizQuestionAnswer.objects.all()
    return render(request, 'quiz_home.html', {'questions': questions})

# Thêm câu hỏi và câu trả lời
def add_question_answer(request):
    if request.method == 'POST':
        form = QuizQuestionAnswerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:quiz_home')
    else:
        form = QuizQuestionAnswerForm()
    return render(request, 'quiz_question_answer_form.html', {'form': form})

# Chỉnh sửa câu hỏi và câu trả lời
def edit_question_answer(request, pk):
    question = get_object_or_404(QuizQuestionAnswer, pk=pk)
    if request.method == 'POST':
        form = QuizQuestionAnswerForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('quiz:quiz_home')
    else:
        form = QuizQuestionAnswerForm(instance=question)
    return render(request, 'quiz_question_answer_form.html', {'form': form})

# Xóa câu hỏi và câu trả lời
def delete_question_answer(request, pk):
    question = get_object_or_404(QuizQuestionAnswer, pk=pk)
    question.delete()
    return redirect('quiz:quiz_home')

# Hiển thị giao diện làm quiz
# def take_quiz(request):
#     questions = QuizQuestionAnswer.objects.all()
#     if request.method == 'POST':
#         total_questions = questions.count()
#         correct_answers = 0

#         user_answers = []  # Danh sách để lưu các câu trả lời của người dùng

#         for question in questions:
#             user_answer = request.POST.get(f'question_{question.id}')
#             if user_answer:  # Kiểm tra nếu người dùng đã chọn câu trả lời
#                 # Tạo đối tượng UserAnswer
#                 user_answer_instance = UserAnswer(question=question, selected_answer=user_answer)
#                 user_answers.append(user_answer_instance)

#                 # Kiểm tra câu trả lời đúng
#                 if user_answer == question.correct_answer:
#                     correct_answers += 1

#         # Lưu tất cả các câu trả lời vào cơ sở dữ liệu
#         UserAnswer.objects.bulk_create(user_answers)

#         score = f'{correct_answers}/{total_questions}'
#         return render(request, 'quiz_result.html', {
#             'score': score,
#             'correct_answers': correct_answers,
#             'total_questions': total_questions
#         })

#     return render(request, 'take_quiz.html', {'questions': questions})



def take_quiz(request):
    questions = QuizQuestionAnswer.objects.all()
    if request.method == 'POST':
        total_questions = questions.count()
        correct_answers = 0

        user_answers = []  # Danh sách để lưu các câu trả lời của người dùng

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer:  # Kiểm tra nếu người dùng đã chọn câu trả lời
                # Tạo đối tượng UserAnswer
                user_answer_instance = UserAnswer(question=question, selected_answer=user_answer)
                user_answers.append(user_answer_instance)

                # Kiểm tra câu trả lời đúng
                if user_answer == question.correct_answer:
                    correct_answers += 1

        # Lưu tất cả các câu trả lời vào cơ sở dữ liệu
        UserAnswer.objects.bulk_create(user_answers)

        score = f'{correct_answers}/{total_questions}'
        return render(request, 'quiz_result.html', {
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'user_answers': user_answers,  # Truyền danh sách câu trả lời của người dùng vào ngữ cảnh
            'questions': questions,  # Truyền danh sách câu hỏi để so sánh câu trả lời
        })

    return render(request, 'take_quiz.html', {'questions': questions})

from django.shortcuts import render

def quiz_grading_list(request):
    user_answers = UserAnswer.objects.all()  # Lấy tất cả câu trả lời của người dùng
    correct_answers = [q.correct_answer for q in QuizQuestionAnswer.objects.all()]

    # Tính số câu đúng
    correct_count = sum(1 for answer in user_answers if answer.selected_answer in correct_answers)
    total_count = len(correct_answers)  # Tổng số câu

    context = {
        'correct_count': correct_count,
        'total_count': total_count,
        'user_answers': user_answers,
    }
    return render(request, 'grading_list.html', context)
