import operator
from django import http
from django.core.urlresolvers import reverse
from django.views.generic import edit, detail, list
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q, Max
from clients.views import ProjectFilterMixin, ProjectItemCreateMixin
from taskboard import models
from taskboard import forms
from tickets.models import Ticket
from history.views import CommentViewMixin, HistoryUpdateMixin

class TaskList(ProjectFilterMixin, list.ListView):
    def get_queryset(self):
        queryset = super(TaskList, self).get_queryset()

        if self.params.get('q'):
            search_fields = ['title', 'description', 'tags']
            words = self.params['q'].split(' ')
            qfilters = []
            for f in search_fields:
                for w in words:
                    qfilters.append(Q(**{'%s__icontains' % f:w}))
            queryset = queryset.filter(reduce(operator.or_, qfilters))

        queryset = queryset.order_by('priority')
        return queryset

class TaskFormMixin(object):
    def get_form_class(self):
        return forms.TaskCreateForm
    
    def get_ticket(self):
        self.ticket = None
        if self.request.GET.get('ticket'):
            ticket_id = self.request.GET['ticket']
            self.ticket = Ticket.objects.get(pk=ticket_id)
        elif self.get_object():
            self.ticket = self.get_object().ticket

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
        initial = super(TaskFormMixin, self).get_initial()

        if self.ticket:
            initial['ticket'] = self.ticket
            initial['title'] = self.ticket.title
            initial['description'] = self.ticket.description
            initial['project'] = self.ticket.project
            initial['due_date'] = self.ticket.due_date
            initial['owner'] = self.ticket.owner

        if Group.objects.count() > 0:
            initial['team'] = Group.objects.all()[0]

        return initial


class TaskUpdate(TaskFormMixin, HistoryUpdateMixin, edit.UpdateView):
    pass

class TaskDetail(CommentViewMixin, detail.DetailView):
    comment_form_class = forms.CommentForm
    
    def save_comment_form(self, comment_form, obj):
        event = super(TaskDetail, self).save_comment_form(comment_form, obj)
        data = comment_form.cleaned_data
        if data['change_status']:
            obj.status = data['change_status']
        if data['closed_reason']:
            obj.closed_reason = data['closed_reason']
        return event

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
    return http.HttpResponse('Successfully moved task {} to {}'.format(pk, to))

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
delete = login_required(edit.DeleteView.as_view(**opts))
list_items = login_required(TaskList.as_view(
        template_name='taskboard/task_list_items.html',
        **list_opts))
