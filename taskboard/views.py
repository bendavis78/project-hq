import operator
from datetime import datetime
from django import http
from django.core.urlresolvers import reverse
from django.views.generic import edit, detail, list
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from clients.views import ProjectFilterMixin, ProjectItemCreateMixin
from taskboard import models, forms, utils
from tickets.models import Ticket
from history.views import CommentViewMixin, HistoryUpdateMixin

class HttpResponseConflict(http.HttpResponse):
    status_code = 409

class HttpResponseJSON(http.HttpResponse):
    def __init__(self, content, mimetype='application/json', status=None):
        import json
        content = json.dumps(content)
        return super(HttpResponseJSON, self).__init__(content, mimetype, status)

class TaskList(ProjectFilterMixin, list.ListView):
    def get_queryset(self, finished=False):
        queryset = super(TaskList, self).get_queryset()

        owner = self.params.get('owner')
        if owner == 'none':
            queryset = queryset.filter(owner=None)
        elif owner:
            queryset = queryset.filter(owner__username=owner)

        if self.params.get('q'):
            search_fields = ['title', 'description', 'tags']
            words = self.params['q'].split(' ')
            qfilters = []
            for f in search_fields:
                for w in words:
                    qfilters.append(Q(**{'%s__icontains' % f:w}))
            queryset = queryset.filter(reduce(operator.or_, qfilters))
        
        # include only finished items for current iteration
        dates = utils.get_iteration_dates(0)
        queryset = queryset.filter(Q(finished_date__isnull=True) |
                                   Q(finished_date__range=dates))

        queryset = queryset.order_by('finished_date', 'priority')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(TaskList, self).get_context_data(*args, **kwargs)
        context = super(TaskList, self).get_context_data(*args, **kwargs)
        current_user = models.TaskUser.from_auth_user(self.request.user)
        context.update({
            'users': models.TaskUser.objects.all(),
            'current_user': current_user,
        })
        return context

class TaskFormMixin(object):
    def get_form_class(self):
        return forms.TaskCreateForm
    
    def get_ticket(self):
        self.ticket = None
        if self.request.GET.get('ticket'):
            ticket_id = self.request.GET['ticket']
            self.ticket = Ticket.objects.get(pk=ticket_id)
        else:
            try:
                self.ticket = self.get_object()
            except AttributeError:
                pass

    def get(self, request, *args, **kwargs):
        self.get_ticket()
        return super(TaskFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_ticket()
        return super(TaskFormMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'ticket': self.ticket,
        }
        kwargs.update(context)
        return super(TaskFormMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('taskboard_index')

class TaskCreate(TaskFormMixin, ProjectItemCreateMixin, edit.CreateView):
    def get_initial(self):
        self.initial = {}
        initial = super(TaskCreate, self).get_initial()

        if self.ticket:
            initial['ticket'] = self.ticket
            initial['title'] = self.ticket.title
            initial['description'] = self.ticket.description
            initial['project'] = self.ticket.project
            initial['due_date'] = self.ticket.due_date
            initial['owner'] = self.ticket.owner

        if models.Team.objects.count() > 0:
            initial['team'] = models.Team.objects.all()[0]

        return initial


class TaskUpdate(TaskFormMixin, HistoryUpdateMixin, edit.UpdateView):
    def get_initial(self):
        self.initial = {}
        return self.initial
        

class TaskDetail(CommentViewMixin, detail.DetailView):
    comment_form_class = forms.CommentForm
    
class TaskDelete(edit.DeleteView):
    def __init__(self, *args, **kwargs):
        kwargs['success_url'] = reverse('taskboard_index')
        super(TaskDelete, self).__init__(*args, **kwargs)

opts = {
    'model': models.Task,
    'context_object_name': 'task',
}
list_opts = opts.copy(); list_opts.update({
    'context_object_name': 'task_list',
})

index = login_required(TaskList.as_view(**list_opts))
create = login_required(TaskCreate.as_view(**opts))
update = login_required(TaskUpdate.as_view(**opts))
detail = login_required(TaskDetail.as_view(**opts))
delete = login_required(TaskDelete.as_view(**opts))
list_items = login_required(TaskList.as_view(
        template_name='taskboard/task_list_items.html',
        **list_opts))
list_item = login_required(TaskDetail.as_view(
        template_name='taskboard/includes/task_list_item.html',
        **opts))

#--| API Functions |-------------------------------------------------------------

def move(request, pk, to):
    task = models.Task.objects.get(pk=pk)
    if to == 'unscheduled':
        task.priority = None
    if to == 'last':
        max = models.Task.objects.aggregate(m=Max('priority'))['m']
        task.priority = (max and max or 0) + 1
    else:
        target = models.Task.objects.get(pk=to)
        if task.priority == target.priority == None:
            return http.HttpResponseForbidden('You cannot prioritize unplanned tasks')
        task.priority = target.priority
    task.save()
    task.log_changes(request.user)
    return http.HttpResponse('Successfully moved task {} to {}'.format(pk, to))

@csrf_exempt
def action(request):
    action = request.POST.get('action')
    #value = request.POST.get('action_value', None)
    ids = request.POST.getlist('ids')
    queryset = models.Task.objects.filter(pk__in=ids)

    # we're looping through each task because we want to log any changes that occur.
    def update_tasks(queryset, **kwargs):
        for task in queryset:
            for attr, value in kwargs.iteritems():
                setattr(task, value)
            task.log_changes(request.user)
            task.save()

    if action == 'unschedule':
        update_tasks(queryset, priority=None)
        msg = 'Successfully unscheduled {} tasks'.format(queryset.count())
    if action == 'start':
        queryset = queryset.filter(finished_date=None, started_date=None)
        update_tasks(queryset, started_date=datetime.today())
        msg = 'Successfully started {} tasks'.format(queryset.count())
    if action == 'finish':
        queryset = queryset.filter(finished_date=None)
        update_tasks(queryset, finished_date=datetime.today())
        msg = 'Successfully finished {} tasks'.format(queryset.count)
    else:
        raise ValueError("Invalid Action: {}".format(action))

    messages.add_message(request, messages.INFO, msg)
    return http.HttpResponseRedirect(reverse('taskboard_index'))

@csrf_exempt
def set_status(request, pk):
    status = request.POST.get('status')
    if not status:
        return http.HttpResponseBadRequest('Status not given')

    if status == 'start':
        task = get_object_or_404(models.Task, pk=pk)
        if task.started_date is not None:
            return HttpResponseConflict('The started date has already been set on this task. You may unset the started date manually.')
        if task.finished_date is not None:
            return HttpResponseConflict('The finished date has already been set on this task. You may unset the finished date manually.')
        task.started_date = datetime.today()
        task.log_changes(request.user)
        task.save()
        response = {
            'task_id': task.id,
            'status': task.status,
            'status_description': task.get_status_description(),
            'started_date': task.started_date.strftime('%Y-%m-%d'),
            'next': 'finish',
            'next_label': 'Finish'
        }

    if status == 'finish':
        task = get_object_or_404(models.Task, pk=pk)
        if task.finished_date is not None:
            return HttpResponseConflict('The finished date has already been set on this task. You may unset the finished date manually.')
        task.finished_date = datetime.today()
        task.log_changes(request.user)
        task.save()
        response = {
            'task_id': task.id,
            'status': task.status,
            'status_description': task.get_status_description(),
            'finished_date': task.finished_date.strftime('%Y-%m-%d'),
            'next': '',
        }
    
    return HttpResponseJSON(response)

@csrf_exempt
def set_effort(request, pk):
    task = get_object_or_404(models.Task, pk=pk)
    if task.finished_date is not None:
        return HttpResponseConflict('Cannot set effort on finished task')
    effort = request.REQUEST.get('effort')
    if not effort:
        return http.HttpResponseBadRequest('Effort parameter not given')
    if effort == 'unestimated':
        if task.status != 'NOT_SCHEDULED' and task.status == 'FINISHED':
            return HttpResponseConflict('Effort cannot be empty on finished tasks.')
        elif task.status != 'NOT_SCHEDULED':
            return HttpResponseConflict('Effort cannot be empty on scheduled tasks.')
        effort = None
    else:
        try:
            effort = int(effort)
        except ValueError:
            effort = ''
        if effort not in [e[0] for e in models.EFFORT_CHOICES]:
            return http.HttpResponseBadRequest('Invalid effort value provided.')
    task.effort = effort
    task.log_changes(request.user)
    task.save()
    return http.HttpResponse('Successfully set effort to {}'.format(effort))

@csrf_exempt
def set_team_strength(request):
    team = request.POST.get('team')
    iteration = request.POST.get('iteration')
    percentage = request.POST.get('percentage')
    try:
        iteration = int(iteration)
    except ValueError:
        iteration = -1
    if iteration < 0 :
        return http.HttpResponseBadRequest('Invalid iteration provided')
    try:
        percentage = int(percentage)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid percentage supplied. Must be a positive integer between or including 0 and 100')
    
    iteration = int(iteration)
    i_start, i_end = utils.get_iteration_dates(iteration)
    try:
        adjustment = models.TeamStrengthAdjustment.objects.get(team=team, start_date=i_start, end_date=i_end)
        adjustment.percentage = percentage
    except models.TeamStrengthAdjustment.DoesNotExist:
        adjustment = models.TeamStrengthAdjustment(team=team, start_date=i_start, end_date=i_end, percentage=percentage)
    adjustment.save()
    return http.HttpResponse('Team strength successfully set to {}% for the dates {} through {}'.format(percentage, i_start, i_end))
