from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context)
