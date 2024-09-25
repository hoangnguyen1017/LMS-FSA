from django.db import models

# Create your models here.

class Exam(models.Model):
    excel_file = models.FileField(upload_to='exams/')  # Lưu tệp Excel đã tải lên
    number_of_exams = models.IntegerField()  # Số lượng kỳ thi được tạo
    generated_at = models.DateTimeField(auto_now_add=True)  # Ngày giờ khi kỳ thi được tạo
    number_of_questions = models.IntegerField()

    def __str__(self):
        return f'Exam created on {self.number_of_questions} with {self.number_of_exams} exams'

    # number_of_questions = models.IntegerField()
    # def __str__(self):
    #     return f'Exam created on {self.generated_at} with {self.number_of_exams} exams'