# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Question, AnswerOption, StudentQuizAttempt, StudentAnswer
from .forms import QuizForm, QuestionFormSet, QuestionForm
from module_group.models import ModuleGroup
from datetime import datetime
import pandas as pd
from django.http import HttpResponse
from subject.models import Subject
from course.models import Course

def quiz_list(request):
    quizzes = Quiz.objects.select_related('course').all()
    module_groups = ModuleGroup.objects.all()
    subjects = Subject.objects.all()
    # Lọc quiz dựa trên subject được chọn
    selected_subject = request.GET.get('subject')
    if selected_subject:
        quizzes = quizzes.filter(course__subject__id=selected_subject)

    context = {
        'module_groups': module_groups,
        'quizzes': quizzes,
        'subjects': subjects,
        'selected_subject': selected_subject,
    }
    return render(request, 'quiz_list.html', context)

def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False) 
            quiz.created_by = request.user  
            quiz.start_datetime = request.POST.get('start_datetime')  
            quiz.end_datetime = request.POST.get('end_datetime')  
            quiz.attempts_allowed = request.POST.get('attempts_allowed')  
            quiz.save()  
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm()
    return render(request, 'quiz_create.html', {'form': form})

def quiz_delete(request, quiz_id):
    # Get the quiz object or return a 404 if not found
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == "POST":
        # Delete the quiz
        quiz.delete()
        
        # Redirect back to the quiz list after deletion
        return redirect('quiz:quiz_list')

    # Render a confirmation page if needed
    return render(request, 'quiz_delete.html', {'quiz': quiz})

def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quiz_edit.html', {'form': form, 'quiz': quiz})



def quiz_question_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    
    return render(request, 'quiz_question_list.html', {'quiz': quiz, 'questions': questions})

def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question_types = ["Multiple Choice", "True/False"]  # Example types

    if request.method == "POST":
        question_id = request.POST.get('question_id')
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points')

        # Validate that the Question ID is unique for this quiz
        if Question.objects.filter(quiz=quiz, id=question_id).exists():
            return render(request, 'quiz/add_question.html', {
                'quiz': quiz,
                'question_id': question_id,
                'question_types': question_types,
                'error': "Question ID must be unique."
            })

        # Create a new question instance
        Question.objects.create(
            quiz=quiz,
            id=question_id,  
            question_text=question_text,
            question_type=question_type,
            points=points
        )

        return redirect('quiz:quiz_question_list', quiz_id=quiz.id)

    context = {
        'quiz': quiz,
        'question_id': '',  # Start empty for user input
        'question_types': question_types,
    }

    return render(request, 'add_question.html', context)


def question_edit(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id)
    question_types = ["Multiple Choice", "True/False"]  # Replace with your actual question types

    if request.method == 'POST':
        new_question_id = request.POST.get('question_id')
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points')

        # Validate that the Question ID is unique for this quiz
        if new_question_id != str(question.id) and Question.objects.filter(quiz=quiz, id=new_question_id).exists():
            return render(request, 'question_edit.html', {
                'quiz': quiz,
                'question': question,
                'question_types': question_types,
                'error': "Question ID must be unique."
            })

        # Update the question instance
        question.id = new_question_id  # Update ID if necessary
        question.question_text = question_text
        question.question_type = question_type
        question.points = points
        question.save()

        return redirect('quiz:quiz_question_list', quiz_id=quiz.id)

    # Pass the current question ID to the context for pre-filling
    context = {
        'quiz': quiz,
        'question': question,
        'question_types': question_types,
        'question_id': question.id,  # Pre-fill with existing ID
    }

    return render(request, 'question_edit.html', context)


def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        question.delete()
        return redirect('quiz:quiz_question_list', quiz_id=question.quiz.id)

    return render(request, 'question_delete.html', {'question': question})


def answer_list(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = AnswerOption.objects.filter(question=question)

    return render(request, 'answer_list.html', {
        'question': question,
        'answers': answers,
    })

def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question_type = question.question_type  # Assuming you have a field for question type

    if request.method == 'POST':
        answer_texts = request.POST.getlist('answer_text[]')
        is_corrects = request.POST.getlist('is_correct[]')  # Ensure you collect all checked values

        for index, answer_text in enumerate(answer_texts):
            is_correct = str(index) in is_corrects  # Check if the answer is marked as correct

            AnswerOption.objects.create(
                question=question,
                option_text=answer_text,
                is_correct=is_correct
            )

        return redirect('quiz:answer_list', question.id)

    return render(request, 'add_answer.html', {'question': question, 'question_type': question_type})

def answer_delete(request, answer_id):
    answer = get_object_or_404(AnswerOption, id=answer_id)
    question_id = answer.question.id  # Get the question ID for redirection
    answer.delete()  
    return redirect('quiz:answer_list', question_id=question_id)


def answer_edit(request, answer_id):
    answer = get_object_or_404(AnswerOption, id=answer_id)
    question_id = answer.question.id  # Get the question ID for redirection

    if request.method == 'POST':
        # Get data from the form
        option_text = request.POST.get('option_text')
        is_correct = request.POST.get('is_correct') == 'on'  # Checkbox value

        # Update the answer
        answer.option_text = option_text
        answer.is_correct = is_correct
        answer.save()

        # Redirect to the list of answers for the question
        return redirect('quiz:answer_list', question_id=question_id)

    # Return the template with the answer's data
    return render(request, 'answer_edit.html', {'answer': answer})


def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()

    # Track the start time of the quiz
    start_time = request.session.get(f'quiz_{quiz_id}_start_time')
    if not start_time:
        request.session[f'quiz_{quiz_id}_start_time'] = str(datetime.now())

    if request.method == "POST":
        # Calculate the time taken by the student
        start_time = datetime.fromisoformat(request.session.get(f'quiz_{quiz_id}_start_time'))
        time_taken = (datetime.now() - start_time).seconds // 60  # Time in minutes
        del request.session[f'quiz_{quiz_id}_start_time']  # Clear start time after submission

        # Create a new attempt
        attempt = StudentQuizAttempt.objects.create(
            user=request.user, 
            quiz=quiz, 
            score=0,  # Initial score
            time_taken=time_taken
        )

        # Loop through each question and save the answers
        for question in questions:
            selected_option_id = request.POST.get(f"question_{question.id}")
            selected_option = get_object_or_404(AnswerOption, id=selected_option_id)
            answer = StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option
            )

        # Call the AI grading function (see below)
        score = grade_quiz(attempt)

        # Update the score for the attempt
        attempt.score = score
        attempt.save()

        # Redirect after completing the quiz
        return redirect('quiz:quiz_result', quiz_id=quiz.id, attempt_id=attempt.id)

    return render(request, 'take_quiz.html', {'quiz': quiz, 'questions': questions, 'time_limit': quiz.time_limit})


def grade_quiz(attempt):
    correct_answers = 0
    total_questions = attempt.studentanswer_set.count()

    for answer in attempt.studentanswer_set.all():
        if answer.selected_option.is_correct:
            correct_answers += 1

    # Calculate score (e.g., 1 point for each correct answer)
    return (correct_answers / total_questions) * 100 if total_questions > 0 else 0


def quiz_result(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id)
    student_answers = StudentAnswer.objects.filter(attempt=attempt)

    # Can add AI grading feedback if needed
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'student_answers': student_answers,
        'attempt': attempt,
    })



def import_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        file = request.FILES['file']
        if file.name.endswith('.xlsx'):
            # Đọc file Excel
            df = pd.read_excel(file)

            # Duyệt từng dòng trong DataFrame
            for index, row in df.iterrows():
                question_text = row['Question']
                question_type = row['Question Type'].strip()  # Lấy loại câu hỏi từ cột Question Type
                correct_answer = row['Correct Answer'].strip().upper()  # Lấy giá trị đúng và chuẩn hóa

                # Kiểm tra loại câu hỏi
                if question_type == "True/False":
                    # Xử lý câu hỏi dạng True/False
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        question_type="True/False",
                        points=10
                    )

                    # Tạo đáp án True và False
                    true_option = AnswerOption.objects.create(
                        question=question,
                        option_text='True',
                        is_correct=(correct_answer == 'A')  # A là đúng nếu đáp án đúng là 'TRUE'
                    )
                    false_option = AnswerOption.objects.create(
                        question=question,
                        option_text='False',
                        is_correct=(correct_answer == 'B')  # B là đúng nếu đáp án đúng là 'FALSE'
                    )

                elif question_type == "Multiple Choice":
                    # Xử lý câu hỏi dạng Multiple Choice

                    answer_options = [
                        str(row['Answer A']).strip().replace('.0', ''),  # Chuyển đổi thành chuỗi và loại bỏ .0
                        str(row['Answer B']).strip().replace('.0', ''),
                        str(row['Answer C']).strip().replace('.0', ''),
                        str(row['Answer D']).strip().replace('.0', '')
                    ]

                    # Tạo câu hỏi mới
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        question_type="Multiple Choice",
                        points=10
                    )

                    # Tạo các đáp án tương ứng cho Multiple Choice
                    for i, answer_text in enumerate(answer_options):
                        option_label = chr(65 + i)  # A, B, C, D tương ứng với 65, 66, 67, 68 trong mã ASCII
                        is_correct = (option_label == correct_answer)

                        AnswerOption.objects.create(
                            question=question,
                            option_text=answer_text,
                            is_correct=is_correct
                        )
                else:
                    # Nếu loại câu hỏi không hợp lệ, bạn có thể xử lý lỗi tại đây
                    continue  # Bỏ qua câu hỏi này hoặc ghi log

            return redirect('quiz:quiz_question_list', quiz_id=quiz.id)

    return render(request, 'import_quiz.html', {'quiz': quiz})




def export_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Tạo danh sách chứa các câu hỏi và đáp án để xuất ra file Excel
    data = []
    
    questions = Question.objects.filter(quiz=quiz)
    for question in questions:
        answer_options = AnswerOption.objects.filter(question=question)

        if question.question_type == "True/False":
            # Nếu là câu hỏi dạng True/False, coi như Multiple Choice với 2 đáp án
            row = {
                "Question": question.question_text,
                "Answer A": answer_options[0].option_text if len(answer_options) > 0 else "",
                "Answer B": answer_options[1].option_text if len(answer_options) > 1 else "",
                "Answer C": "",
                "Answer D": "",
                "Correct Answer": ""
            }

            # Xác định đáp án đúng
            for i, option in enumerate(answer_options):
                if option.is_correct:
                    row["Correct Answer"] = chr(65 + i)  # 65 là mã ASCII cho 'A'
            
            row["Question Type"] = "True/False"
        else:
            # Nếu là câu hỏi dạng Multiple Choice
            row = {
                "Question": question.question_text,
                "Answer A": answer_options[0].option_text if len(answer_options) > 0 else "",
                "Answer B": answer_options[1].option_text if len(answer_options) > 1 else "",
                "Answer C": answer_options[2].option_text if len(answer_options) > 2 else "",
                "Answer D": answer_options[3].option_text if len(answer_options) > 3 else "",
                "Correct Answer": ""
            }

            # Xác định đáp án đúng
            for i, option in enumerate(answer_options):
                if option.is_correct:
                    row["Correct Answer"] = chr(65 + i)  # 65 là mã ASCII cho 'A'

            row["Question Type"] = "Multiple Choice"

        data.append(row)

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data)

    # Tạo response dưới dạng file Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=quiz_{quiz_id}.xlsx'

    # Xuất file Excel
    df.to_excel(response, index=False, engine='openpyxl')

    return response
