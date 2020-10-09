from django.shortcuts import render
from .file import *
from pathlib import Path


def home(request):
    if request.method == 'POST':
        file_name = request.POST.get('fileName')
        if file_name is None or file_name == '':
            return render(request, 'app.html')
        else:
            return render(request, 'app.html', {
                'file_name': file_name,
                'data_file': read_file(file_name)
            })
    else:
        return render(request, 'app.html')
