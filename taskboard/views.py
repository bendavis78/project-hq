from django import http
from django.core.urlresolvers import reverse
from django.views.generic import edit, detail, list
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from clients.views import ProjectFilterMixin, ProjectItemCreateMixin
from taskboard import models
from taskboard import forms
from tickets.models import Ticket
from history.views import CommentViewMixin, HistoryUpdateMixin

class TaskList(ProjectFilterMixin, list.ListView):
    pass

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

    def get_initial(self):
        initial = super(TaskFormMixin, self).get_initial()

        if self.get_object():
            return initial

        if self.ticket:
            initial['ticket'] = self.ticket
            initial['title'] = self.ticket.title
            initial['description'] = self.ticket.description
            initial['project'] = self.ticket.project

        if Group.objects.count() > 0:
            initial['team'] = Group.objects.all()[0]

        return initial

    def get_context_data(self, **kwargs):
        context = {
            'ticket': self.ticket,
        }
        kwargs.update(context)
        return super(TaskFormMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('taskboard_index')

class TaskCreate(TaskFormMixin, ProjectItemCreateMixin, edit.CreateView):
    pass

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
    target = models.Task.objects.get(pk=to)
    task.priority = target.priority
    task.save()
    return http.HttpResponse('')

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
