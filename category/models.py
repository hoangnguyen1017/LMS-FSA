from django.db import models
from subject.models import Subject
from django.core.exceptions import ValidationError

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, related_name='categories', blank=True)

    class Meta:
        unique_together = ('category_name',)

    def __str__(self):
        return self.category_name

    def get_descendants(self):
        descendants = set()
        subs = self.subcategories.all()
        for sub in subs:
            descendants.add(sub)
            descendants.update(sub.get_descendants())
        return descendants

    def save(self, *args, **kwargs):
        self.category_name = self.category_name.lower()
        super().save(*args, **kwargs)
        self.update_subcategories_subjects()

    def update_subcategories_subjects(self):
        for subcategory in self.subcategories.all():
            subcategory.subjects.set(self.subjects.all())
            subcategory.save()

class SubCategory(models.Model):
    subcategory_name = models.CharField(max_length=255)
    parent_category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('subcategory_name', 'parent_category')

    def __str__(self):
        return self.subcategory_name

    def clean(self):
        # Check if a category with the same name exists (case-sensitive)
        if Category.objects.filter(category_name__exact=self.subcategory_name).exists():
            raise ValidationError("A category with this exact name already exists.")

    def save(self, *args, **kwargs):
        self.subcategory_name = self.subcategory_name.lower()
        self.clean()
        super().save(*args, **kwargs)
        # Inherit subjects from parent category
        self.subjects.set(self.parent_category.subjects.all())

    @property
    def subjects(self):
        return self.parent_category.subjects