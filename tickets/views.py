from django.views.generic import list, edit, detail

from tickets import models

class TicketList(list.ListView):
    archive = False

    def get_queryset(self):
        queryset = super(TicketList, self).get_queryset()
        if self.archive:
            return queryset.filter(status='CLOSED')
        return queryset.exclude(status='CLOSED')

opts = {
    'model': models.Ticket,
    'context_object_name': 'ticket',
}
list_opts = opts.copy(); list_opts.update({
    'context_object_name': 'ticket_list',
})

index = TicketList.as_view(**list_opts)
archive = TicketList.as_view(**opts)
create = edit.CreateView.as_view(**opts)
update = edit.UpdateView.as_view(**opts)
delete = edit.DeleteView.as_view(**opts)
detail = detail.DetailView.as_view(**opts)
