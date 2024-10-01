from django import forms
from django.core.exceptions import ValidationError
from .models import Category, SubCategory  # Import SubCategory
from subject.models import Subject  # Make sure this import is present


# Form để tạo/chỉnh sửa Category
class CategoryForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Category
        fields = ['category_name', 'subjects']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['subjects'].initial = self.instance.subjects.all()

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].lower()
        if Category.objects.filter(category_name__iexact=category_name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A category with this name already exists (case-insensitive).")
        return category_name

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            category.save()
            self.save_m2m()
            category.update_subcategories_subjects()
        return category


# Form đơn giản để tạo Subcategory
class SubCategoryForm(forms.ModelForm):
    parent_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True
    )

    class Meta:
        model = SubCategory
        fields = ['subcategory_name', 'parent_category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_category'].label_from_instance = lambda obj: obj.category_name
        self.fields['parent_category'].error_messages = {
            'required': 'Please select a parent category.',
            'invalid_choice': 'Please select a valid parent category.'
        }

    def clean(self):
        cleaned_data = super().clean()
        subcategory_name = cleaned_data.get('subcategory_name', '').lower()
        parent_category = cleaned_data.get('parent_category')

        if subcategory_name and parent_category:
            # Check if a subcategory with the same name exists under the same parent category (case-insensitive)
            if SubCategory.objects.filter(subcategory_name__iexact=subcategory_name,
                                          parent_category=parent_category).exclude(pk=self.instance.pk).exists():
                raise ValidationError(
                    "A subcategory with this name already exists under the selected parent category (case-insensitive).")

            # Check if a category with the same name exists (case-insensitive)
            if Category.objects.filter(category_name__iexact=subcategory_name).exists():
                raise ValidationError("A category with this name already exists (case-insensitive).")

        cleaned_data['subcategory_name'] = subcategory_name
        return cleaned_data

    def save(self, commit=True):
        subcategory = super().save(commit=False)
        if commit:
            subcategory.save()
            subcategory.update_subjects()
        return subcategory

    def update_subjects(self):
        parent_category = self.cleaned_data.get('parent_category')
        if parent_category:
            self.instance.subjects.set(parent_category.subjects.all())
