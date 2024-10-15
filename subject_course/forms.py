from django import forms
from .models import Material, Lesson, Course

# Form for creating/editing a Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']


# Form for creating/editing a Lesson, linking it to a Course
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'description', 'content']  # Include 'course' and 'content' (RichTextField)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'ckeditor'}),
        }


# Form for adding Materials to a Lesson
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['lesson', 'material_type', 'file']
