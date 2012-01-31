from django import http
from django.views.generic import list, edit, detail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from clients.models import Project, Client
from tickets import models

class TicketList(list.ListView):
    archive = False

    def get(self, request, *args, **kwargs):
        self.params = request.GET.copy()

        self.client = None
        self.project = None

        if self.params.get('project'):
            self.project = Project.objects.get(pk=self.params['project'])

        if self.params.get('client'):
            self.client = Client.objects.get(pk=self.params['client'])
        
        if self.client and self.project and self.project.client != self.client:
            return http.HttpResponseRedirect('./?client={}'.format(self.client.pk))

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

        elif self.client:
            queryset = queryset.filter(project__client=self.client)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(TicketList, self).get_context_data(*args, **kwargs)
        clients = Client.objects.order_by('name')
        projects = Project.objects.order_by('name')

        if self.client:
            projects = projects.filter(client=self.client)

        context.update({
            'params': self.params,
            'current_project': self.project,
            'current_client': self.client,
            'projects': projects,
            'clients': clients,
            'users': User.objects.all(),
        })
        return context


class TicketCreate(edit.CreateView):
    def get_initial(self):
        return {
            'submitted_by': self.request.user,
        }


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
update = login_required(edit.UpdateView.as_view(**opts))
delete = login_required(edit.DeleteView.as_view(**opts))
detail = login_required(detail.DetailView.as_view(**opts))
