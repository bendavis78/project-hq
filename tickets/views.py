from django.views.generic import list, edit, detail
from django.contrib.auth.decorators import login_required

from tickets import models

class TicketList(list.ListView):
    archive = False

    def get_queryset(self):
        queryset = super(TicketList, self).get_queryset()
        if self.archive:
            queryset = queryset.filter(status='CLOSED')
        queryset = queryset.exclude(status='CLOSED')

        if self.request.GET.get('owner') == 'none':
            queryset = queryset.filter(owner=None)
        elif self.request.GET.get('owner') == 'me':
            queryset = queryset.filter(owner=self.request.user)

        if self.request.GET.get('status') == 'assigned':
            queryset = queryset.filter(status='ASSIGNED')
        elif self.request.GET.get('status') == 'new':
            queryset = queryset.filter(status='NEW')

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(TicketList, self).get_context_data(*args, **kwargs)
        context.update({
            'params': self.request.GET,
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
