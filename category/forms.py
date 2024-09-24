from django import forms
from django.core.exceptions import ValidationError
from .models import Category


class CategoryForm(forms.ModelForm):
    subs = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Category
        fields = ['category_name', 'subs']

    def clean_subs(self):
        subs = self.cleaned_data.get('subs')
        if self.instance:
            if self.instance in subs:
                raise ValidationError("A category cannot be its own subcategory.")
            for sub in subs:
                if sub in self.instance.get_descendants():
                    raise ValidationError("A category cannot be a subcategory of its descendant.")
        return subs
