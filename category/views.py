from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, SubCategory
from .forms import CategoryForm, SubCategoryForm
from module_group.models import ModuleGroup
from django.contrib import messages

# Category views
def category_list(request):
    categories = Category.objects.all().prefetch_related('subjects', 'subcategories')
    return render(request, 'category_list.html', {
        'categories': categories,
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'category_detail.html', {'category': category})

def category_add(request):
    if request.method == 'POST':
        if 'create_subcategory' in request.POST:
            subcategory_form = SubCategoryForm(request.POST)
            if subcategory_form.is_valid():
                subcategory = subcategory_form.save()
                messages.success(request, 'Subcategory created successfully.')
                return redirect('category:category_add')
            else:
                for field, errors in subcategory_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Subcategory {field}: {error}")
                form = CategoryForm()
        else:
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                messages.success(request, 'Category created successfully.')
                return redirect('category:category_add')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Category {field}: {error}")
            subcategory_form = SubCategoryForm()
    else:
        form = CategoryForm()
        subcategory_form = SubCategoryForm()

    return render(request, 'category_form.html', {
        'form': form,
        'subcategory_form': subcategory_form
    })

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category:category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

# Xử lý sửa Category
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            category.update_subcategories_subjects()
            return redirect('category:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

def subcategory_edit(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            subcategory = form.save()
            return redirect('category:category_list')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'category_form.html', {'form': form, 'is_subcategory': True, 'subcategory': subcategory})

def subcategory_delete(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('category:category_list')
    return render(request, 'category_confirm_delete.html', {'subcategory': subcategory})