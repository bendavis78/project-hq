import operator
from django import http
from django.views.generic import edit, detail, list
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        elif owner == 'me':
            queryset = queryset.filter(owner=self.request.user)
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
        context.update({
            'statuses': TICKET_STATUS_CHOICES,
            'closed_reasons': TICKET_CLOSED_REASONS,
            'users': User.objects.all(),
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
