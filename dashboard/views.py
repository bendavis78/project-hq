from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket
from taskboard.models import Task
from taskboard import utils

@login_required
def index(request):
    remaining_tasks = Task.objects.filter(iteration=0, finished_date__isnull=True)
    unscheduled_tasks = Task.objects.filter(priority__isnull=True)
    new_tickets = Ticket.objects.filter(status='NEW')
    user_tasks = Task.objects.filter(iteration=0, owner=request.user)
    user_tasks = user_tasks.order_by('finished_date','priority')
    user_tickets = Ticket.objects.filter(owner=request.user)
    user_tickets = user_tickets.filter(status__in=('ASSIGNED','FEEDBACK','NEW'))
    iteration_dates = utils.get_iteration_dates(0)
    unassigned_tickets = Ticket.objects.filter(owner=None)
    context = {
        'new_tickets': new_tickets,
        'remaining_tasks': remaining_tasks,
        'unscheduled_tasks': unscheduled_tasks,
        'iteration_dates': iteration_dates,
        'user_tickets': user_tickets,
        'user_tasks': user_tasks,
        'unassigned_tickets': unassigned_tickets,
    }
    return render(request, 'dashboard/index.html', context)
