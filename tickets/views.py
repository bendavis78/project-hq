from datetime import datetime
from django import http
from django.views.generic import list, edit, detail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from clients.models import Project, Client
from tickets import models
from tickets import forms

class TicketList(list.ListView):
    archive = False

    def get(self, request, *args, **kwargs):
        self.params = request.GET.copy()

        self.client = None
        self.project = None
        self.all_client = None

        if self.params.get('project'):
            if self.params['project'].startswith('all_'):
                self.all_client = int(self.params['project'].replace('all_', ''))
            else:
                self.project = Project.objects.get(pk=self.params['project'])
        
        return super(TicketList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(TicketList, self).get_queryset()
        if self.archive:
            queryset = queryset.filter(status='CLOSED')
        queryset = queryset.exclude(status='CLOSED')
        
        owner = self.params.get('owner')
        if owner == 'none':
            queryset = queryset.filter(owner=None)
        elif owner == 'me':
            queryset = queryset.filter(owner=self.request.user)
        elif owner:
            queryset = queryset.filter(owner__username=owner)

        if self.params.get('status') == 'assigned':
            queryset = queryset.filter(status='ASSIGNED')
        elif self.params.get('status') == 'new':
            queryset = queryset.filter(status='NEW')

        if self.project:
            queryset = queryset.filter(project=self.project)
        elif self.all_client:
            queryset = queryset.filter(project__client=self.all_client)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(TicketList, self).get_context_data(*args, **kwargs)
        clients = Client.objects.order_by('name')
        
        context.update({
            'params': self.params,
            'current_project': self.project,
            'clients': clients,
            'users': User.objects.all(),
            'all_client': self.all_client,
        })
        return context


class TicketCreate(edit.CreateView):
    def get_initial(self):
        return {
            'submitted_by': self.request.user,
        }


class TicketDetail(detail.DetailView):
    def get_context_data(self, **kwargs):
        context = super(TicketDetail, self).get_context_data(**kwargs)
        ticket = self.object
        if self.request.method == 'POST':
            self.comment_form = forms.CommentForm(self.request.POST)
            if self.comment_form.is_valid():
                data = self.comment_form.cleaned_data
                comment = None
                event = models.TicketEvent(ticket=self, user=self.request.user).save()
                if data['comment']:
                    comment = models.TicketComment(event=event, messave=data['comment'])
                    comment.save()
                if data['change_status']:
                    ticket.status = data['change_status']
                if data['closed_reason']:
                    ticket.closed_reason = data['closed_reason']
                ticket.log_changes(event)
                ticket.save()
        else:
            self.comment_form = forms.CommentForm(initial={'ticket':ticket})
        context.update({
            'comment_form': self.comment_form,
        })
        return context

class TicketUpdate(edit.UpdateView):
    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.log_changes(self.request.user)
        return super(TicketUpdate, self).form_valid(form)
    
opts = {
    'model': models.Ticket,
    'context_object_name': 'ticket',
}
list_opts = opts.copy(); list_opts.update({
    'context_object_name': 'ticket_list',
})

index = login_required(TicketList.as_view(**list_opts))
archive = login_required(TicketList.as_view(**opts))
create = login_required(TicketCreate.as_view(**opts))
update = login_required(TicketUpdate.as_view(**opts))
detail = login_required(TicketDetail.as_view(**opts))
delete = login_required(edit.DeleteView.as_view(**opts))
