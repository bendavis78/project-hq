import operator
from django import http
from django.views.generic import edit, detail, list
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from clients.views import ProjectFilterMixin, ProjectItemCreateMixin
from tickets import models
from tickets import forms
from tickets.models import TICKET_STATUS_CHOICES, TICKET_CLOSED_REASONS
from history.views import CommentViewMixin, HistoryUpdateMixin

class TicketList(ProjectFilterMixin, list.ListView):
    archive = False

    def get_queryset(self):
        queryset = super(TicketList, self).get_queryset()
        if self.archive:
            queryset = queryset.filter(status='CLOSED')
            if self.params.get('closed_reason'):
                queryset = queryset.filter(closed_reason=self.params['closed_reason'])
        else:
            queryset = queryset.exclude(status='CLOSED')
        
        owner = self.params.get('owner')
        if owner == 'none':
            queryset = queryset.filter(owner=None)
        elif owner:
            queryset = queryset.filter(owner__username=owner)

        if self.params.get('status'):
            queryset = queryset.filter(status=self.params.get('status'))

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

    def get_context_data(self, *args, **kwargs):
        context = super(TicketList, self).get_context_data(*args, **kwargs)
        current_user = models.TicketUser.from_auth_user(self.request.user)
        context.update({
            'statuses': TICKET_STATUS_CHOICES,
            'closed_reasons': TICKET_CLOSED_REASONS,
            'users': models.TicketUser.objects.all(),
            'current_user': current_user,
            'archive': self.archive,
        })
        return context


class TicketCreate(ProjectItemCreateMixin, edit.CreateView):
    pass

class TicketDetail(CommentViewMixin, detail.DetailView):
    comment_form_class = forms.CommentForm
    
    def save_comment_form(self, comment_form, obj):
        event = super(TicketDetail, self).save_comment_form(comment_form, obj)
        data = comment_form.cleaned_data
        if data['change_status']:
            obj.status = data['change_status']
        if data['closed_reason']:
            obj.closed_reason = data['closed_reason']
        return event

class TicketUpdate(HistoryUpdateMixin, edit.UpdateView):
    pass

def move(request, pk, to):
    ticket = models.Ticket.objects.get(pk=pk)
    target = models.Ticket.objects.get(pk=to)
    ticket.priority = target.priority
    ticket.save()
    return http.HttpResponse('')
    
def action(request):
    action = request.POST.get('action')
    value = request.POST.get('action_value', None)
    ids = request.POST.getlist('ids')
    queryset = models.Ticket.objects.filter(pk__in=ids)
    count = queryset.count()
    msg = None

    if action == 'set-status':
        if 'CLOSED-' in value:
            closed_reason = value.split('-')[1]
            queryset.update(status='CLOSED', closed_reason=closed_reason)
        else:
            queryset.update(status=value)
        msg = "Successfully set status on {} tickets to {}".format(count, value)
        messages.add_message(request, messages.INFO, msg)

    elif action == 'convert-task':
        from taskboard.models import Task, TaskUser
        from django.contrib.auth.models import Group
        count_success = 0
        count_failed = 0
        for ticket in queryset:
            try:
                ticket.task
            except Task.DoesNotExist:
                task = Task(ticket=ticket)
                task.title = ticket.title
                task.desscription = ticket.description
                task.project = ticket.project
                task.due_date = ticket.due_date
                task.team = Group.objects.all()[0]
                task.effort = 0
                task.owner = None
                task.priority = None
                if ticket.owner:
                    owner = TaskUser()
                    owner.__dict__ = ticket.owner.__dict__
                    task.owner = owner
                task.save()
                count_success += 1
            else:
                count_failed += 1

        if count_success > 0:
            msg = "Successfully converted {} tickets to tasks.".format(count_success)
            messages.add_message(request, messages.INFO, msg)
        if count_failed > 0:
            msg = "Some tickets were not converted to tasks because they've already been converted."
            messages.add_message(request, messages.WARNING, msg)


    else:
        raise ValueError("Invalid Action: {}".format(action))

    return http.HttpResponseRedirect(reverse('tickets_index'))

opts = {
    'model': models.Ticket,
    'context_object_name': 'ticket',
}
list_opts = opts.copy(); list_opts.update({
    'context_object_name': 'ticket_list',
})
archive_opts = list_opts.copy(); archive_opts.update({
    'archive': True
})

index = login_required(TicketList.as_view(**list_opts))
archive = login_required(TicketList.as_view(**archive_opts))
create = login_required(TicketCreate.as_view(**opts))
update = login_required(TicketUpdate.as_view(**opts))
detail = login_required(TicketDetail.as_view(**opts))
delete = login_required(edit.DeleteView.as_view(**opts))
