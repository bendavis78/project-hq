from clients.models import Project, Client

class ProjectFilterMixin(object):

    def get(self, request, *args, **kwargs):
        self.params = request.GET.copy() or request.session.get('last_filter', {})
        if self.params != request.session.get('last_filter', {}):
            request.session['last_filter'] = self.params

        self.client = None
        self.project = None
        self.all_client = None
        
        # params set to "__all__" signal a reset to empty
        for k, v in self.params.iteritems():
            if v == '__all__':
                del self.params[k]

        if self.params.get('project'):
            if self.params['project'].startswith('all_'):
                self.all_client = int(self.params['project'].replace('all_', ''))
            else:
                self.project = Project.objects.get(pk=self.params['project'])

        return super(ProjectFilterMixin, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(ProjectFilterMixin, self).get_queryset()
        if self.project:
            queryset = queryset.filter(project=self.project)
        elif self.all_client:
            queryset = queryset.filter(project__client=self.all_client)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectFilterMixin, self).get_context_data(*args, **kwargs)
        clients = Client.objects.order_by('name')
        context.update({
            'params': self.params,
            'current_project': self.project,
            'clients': clients,
            'all_client': self.all_client,
        })
        return context

class ProjectItemCreateMixin(object):
    def get_initial(self):
        self.initial = {}
        initial = super(ProjectItemCreateMixin, self).get_initial()
        if initial is None:
            initial = {}
        current_filter = self.request.session.get('last_filter', None)
        project = None
        if current_filter:
            project = current_filter.get('project', None)
        initial.update({
            'submitted_by': self.request.user,
            'project': project,
        })
        return initial
