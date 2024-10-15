# from import_export import resources
# from .models import Subject, Category, SubCategory, Material

# class SubjectResource(resources.ModelResource):
#     class Meta:
#         model = Subject
#         fields = ('id', 'name', 'description', 'code')  # Specify the fields you want to export/import
#         export_order = ('id', 'name', 'description', 'code')

# class CategoryResource(resources.ModelResource):
#     class Meta:
#         model = Category
#         fields = ('id', 'category_name', 'subject__name')  # Export subject name instead of FK
#         export_order = ('id', 'category_name', 'subject__name')

# class MaterialResource(resources.ModelResource):
#     class Meta:
#         model = Material
#         fields = ('id', 'subject__name', 'material_type', 'file', 'uploaded_at')  # Export subject name instead of FK
#         export_order = ('id', 'subject__name', 'material_type', 'file', 'uploaded_at')

