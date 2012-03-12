from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context)
