from django.shortcuts import render
from django import forms
import json
import pandas as pd
from django.http import HttpResponse
from .forms import ExcelUploadForm ,WordUploadForm
import zipfile
from tools.libs.utils import excel_to_json
import os
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from tools.libs.utils import excel_to_json, word_to_json
from tools.libs import txtToJson
def excel_to_json_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []

            for excel_file in form.cleaned_data['files']:  # Sử dụng cleaned_data
                try:
                    # Đọc dữ liệu từ file Excel
                    excel_data = pd.read_excel(excel_file, sheet_name=None)  # Đọc toàn bộ sheets của file Excel
                    print(f"EXCEL_DATA IS :{excel_data}")

                    for sheet_name, df in excel_data.items():
                        # Convert the sheet to JSON
                        json_output = excel_to_json(df)  # excel_to_json() expects a DataFrame
                        print(json_output)

                        # Create a separate JSON file for each sheet
                        json_filename = f"{excel_file.name.split('.')[0]}_{sheet_name}.json"
                        # json_string = json.dumps(json_output, indent=4, ensure_ascii=False)
                        json_files.append((json_filename, json_output))  # Append each sheet's JSON to the list

                except Exception as e:
                    print(f"Lỗi khi xử lý tệp Excel '{excel_file.name}': {e}")

            # Tạo tệp ZIP để chứa tất cả các file JSON
            file_name_without_extension = os.path.splitext(excel_file.name)[0]
            zip_filename = file_name_without_extension + '_converted.zip' 
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

            with zipfile.ZipFile(response, 'w') as zip_file:
                for json_filename, json_string in json_files:
                    # Add each JSON file for each sheet to the ZIP
                    zip_file.writestr(json_filename, json_string)

            return response

    else:
        form = ExcelUploadForm()

    return render(request, 'tool_excel_to_json.html', {'form': form})


from .libs.txtToJson import txt_to_json
from docx import Document 
# Sử dụng hàm này trong hàm upload_file
def read_docx_content(file):
    """Đọc nội dung từ tệp .docx."""
    document = Document(file)  # Mở tệp .docx
    content = []  # Khởi tạo danh sách để lưu nội dung

    # Lặp qua tất cả các đoạn văn bản trong tài liệu
    for paragraph in document.paragraphs:
        content.append(paragraph.text)  # Thêm nội dung đoạn văn vào danh sách

    # Kết hợp tất cả nội dung thành một chuỗi, mỗi đoạn cách nhau bởi dấu xuống dòng
    return "\n".join(content)
def word_to_json_view(request):
    if request.method == 'POST':
        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            
            for uploaded_file in form.cleaned_data['files']:
                try:
                    if uploaded_file.name.endswith('.txt'):
                        # Xử lý tệp .txt và chuyển đổi sang JSON
                        json_output = txt_to_json(uploaded_file, uploaded_file.name)
                        
                        json_filename = f"{uploaded_file.name.split('.')[0]}.json"
                        json_files.append((json_filename, json_output))
                    elif uploaded_file.name.endswith('.docx'):
                        # Đọc nội dung từ tệp .docx và chuyển đổi sang JSON
                        docx_content = read_docx_content(uploaded_file)
                        json_output = txt_to_json(docx_content, uploaded_file.name)  # Chuyển đổi nội dung text sang JSON
                        json_filename = f"{uploaded_file.name.split('.')[0]}.json"
                        json_files.append((json_filename, json_output))


                except Exception as e:
                    print(f"Lỗi khi xử lý tệp TXT '{uploaded_file.name}': {e}")

            # Tạo tệp ZIP để chứa tất cả các file JSON
            file_name_without_extension = os.path.splitext(uploaded_file.name)[0]
            zip_filename = file_name_without_extension + '_converted.zip'
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

            with zipfile.ZipFile(response, 'w') as zip_file:
                for json_filename, json_string in json_files:
                    # Thêm mỗi file JSON vào ZIP
                    zip_file.writestr(json_filename, json_string)

            return response
    else:
        form = WordUploadForm()

    return render(request, 'tool_word_to_json.html', {'form': form})
def view_tools(request):
    return render(request,'view_tools.html')