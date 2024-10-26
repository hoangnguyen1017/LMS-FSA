from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import ExcelUploadForm, WordUploadForm
from tools.libs.utils import excel_to_json, word_to_json
import pandas as pd
import os
import zipfile


def view_tools(request):
    # Assuming you have a list of tools defined somewhere in your views or imported
    tools = [
        {'name': 'Excel to JSON', 'url': '/excel_to_json_view/'},
        {'name': 'Word to JSON', 'url': '/word_to_json_view/'},
        # Add more tools as needed
    ]
    
    return render(request, 'view_tools.html', {'tools': tools})


def excel_to_json_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            for excel_file in form.cleaned_data['files']:
                try:
                    json_files.extend(process_excel_file(excel_file))
                except Exception as e:
                    print(f"Error processing '{excel_file.name}': {e}")
                    return JsonResponse({'error': f'Error processing {excel_file.name}: {str(e)}'}, status=400)

            zip_filename = create_zip_from_json_files(json_files)
            return download_zip_file(zip_filename)
    else:
        form = ExcelUploadForm()
    return render(request, 'tool_excel_to_json.html', {'form': form})

def process_excel_file(excel_file):
    excel_data = pd.read_excel(excel_file, sheet_name=None)
    json_files = []
    for sheet_name, df in excel_data.items():
        json_output = excel_to_json(df)
        json_filename = f"{excel_file.name.split('.')[0]}_{sheet_name}.json"
        json_files.append((json_filename, json_output))
    return json_files

def create_zip_from_json_files(json_files):
    zip_filename = 'exported_json_files.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for json_filename, json_output in json_files:
            zipf.writestr(json_filename, json_output)
    return zip_filename

def download_zip_file(zip_filename):
    if os.path.exists(zip_filename):
        with open(zip_filename, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        # Optionally, delete the zip file after download to save space
        os.remove(zip_filename)
        return response
    else:
        return JsonResponse({'error': 'Zip file not found'}, status=404)

def word_to_json_view(request):
    if request.method == 'POST':
        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            for word_file in form.cleaned_data['files']:
                try:
                    json_files.extend(process_word_file(word_file))
                except Exception as e:
                    print(f"Error processing '{word_file.name}': {e}")
                    return JsonResponse({'error': f'Error processing {word_file.name}: {str(e)}'}, status=400)

            zip_filename = create_zip_from_json_files(json_files)
            return download_zip_file(zip_filename)
    else:
        form = WordUploadForm()
    return render(request, 'tool_word_to_json.html', {'form': form})

def process_word_file(word_file):
    try:
        json_output = word_to_json(word_file)  # Assuming word_to_json handles a single file
        json_filename = f"{word_file.name.split('.')[0]}.json"
        return [(json_filename, json_output)]
    except Exception as e:
        raise Exception(f"Failed to convert {word_file.name}: {str(e)}")
