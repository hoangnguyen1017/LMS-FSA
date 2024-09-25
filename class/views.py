from django.shortcuts import render, redirect
from .models import ClassInfo,Student
from .forms import ClassInfoForm,StudentForm
from django.shortcuts import render, get_object_or_404, redirect
def add_class(request):
    if request.method == "POST":
        form = ClassInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class:class_list')  
    else:
        form = ClassInfoForm()
    return render(request, 'add_class.html', {'form': form})

def class_edit(request,pk):
    class_ne = get_object_or_404(ClassInfo , pk=pk)
    if request.method=='POST':
            form = ClassInfoForm(request.POST,instance=class_ne )
            if form.is_valid():
                 form.save()
                 return redirect('class:class_list')
    else:
         form = ClassInfoForm(instance=class_ne)
    return render(request , 'class_form.html' , {'form':form})

def class_delete(request,pk):
     class_ne = get_object_or_404(ClassInfo , pk=pk)
     if request.method == 'POST':
        class_ne.delete()
        return redirect('class:class_list')
     return render(request, 'class_confirm_delete.html', {'class': class_ne})


def class_list(request):
    classes = ClassInfo.objects.all()
    return render(request, 'class_list.html', {'classes': classes})



#---------------------------------
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)  # Tạo đối tượng Student nhưng không lưu ngay
            student.save()  
            student.class_info.number_student += 1  # Tăng số sinh viên trong lớp
            student.class_info.save()  
            return redirect('class:class_list')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('class:class_list')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'student_edit.html', {'form': form, 'student': student})
