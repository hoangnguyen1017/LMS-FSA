from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from quiz.models import Quiz, Question, AnswerOption, StudentQuizAttempt, StudentAnswer
from course.models import Course
from django.db import transaction
from django.utils import timezone

# Create your views here.
@login_required
def quiz_list(request):
    courses = Course.objects.all()
    quizzes = Quiz.objects.all()  # Start with all quizzes

    selected_course = request.GET.get('course')
    if selected_course:
        quizzes = quizzes.filter(course__id=selected_course)  # Correct filter

    # Sort quizzes by name (or any other field you want)
    quizzes = quizzes.order_by('quiz_title')  
    courses = courses.order_by('course_name')
    context = {
        'quizzes': quizzes,
        'courses': courses,
        'selected_course': selected_course,
    }
    return render(request, 'quiz_list_student.html', context)


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_detail_student.html', {'quiz': quiz, 'questions': questions})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()  # Lấy tất cả các câu hỏi trong quiz

    if request.method == 'POST':
        # Khi người dùng gửi form (submit quiz)
        with transaction.atomic():
            # Tạo một lần thử quiz mới cho học sinh
            attempt = StudentQuizAttempt.objects.create(user=request.user, quiz=quiz, score=0.0)

            total_score = 0
            for question in questions:
                selected_option_id = request.POST.get(f'question_{question.id}')  # Lấy lựa chọn được chọn cho câu hỏi
                text_response = request.POST.get(f'text_response_{question.id}')  # Thay đổi tên ở đây
                # Nếu câu hỏi là một câu hỏi dạng text, không cần truy xuất selected_option
                selected_option = None
                if selected_option_id and selected_option_id.isdigit():
                    selected_option = AnswerOption.objects.get(id=int(selected_option_id))
                # Lưu câu trả lời của học sinh
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    text_response=text_response 
                )

                # Kiểm tra nếu lựa chọn đúng, cộng điểm
                if selected_option and selected_option.is_correct:
                    total_score += question.points

            # Cập nhật điểm tổng của lần thử
            attempt.score = total_score
            attempt.save()

            return redirect('quiz:quiz_result', quiz_id=quiz.id, attempt_id=attempt.id)  # Chuyển tới trang kết quả sau khi nộp bài

    # Render trang quiz với câu hỏi và lựa chọn
    return render(request, 'take_quiz_student.html', {'quiz': quiz, 'questions': questions})

@login_required
def quiz_result(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id, user=request.user)
    student_answers = StudentAnswer.objects.filter(attempt=attempt)

    return render(request, 'quiz_result_student.html', {
        'quiz' : quiz,
        'attempt': attempt,
        'student_answers': student_answers,
    })