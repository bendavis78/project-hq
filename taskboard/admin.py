#from django.contrib import admin
#from orderable.admin import OrderableAdmin
#from . import models
#from . import utils
#
#class CompletedListFilter(admin.SimpleListFilter):
#    title = "Completed"
#    parameter_name='is_completed'
#
#    def lookups(self, request, model_admin):
#        pass
#    def has_output(self):
#        return True
#
#    def choices(self, cl):
#        return ({
#            'selected': self.value() is None,
#            'query_string': cl.get_query_string({}, [self.parameter_name]),
#            'display': 'Incomplete'
#        }, {
#            'selected': self.value() == '1',
#            'query_string': cl.get_query_string({self.parameter_name: '1'}, []),
#            'display': 'Completed'
#        }, {
#            'selected': self.value() == '2',
#            'query_string': cl.get_query_string({self.parameter_name: '2'},[]),
#            'display': 'All'
#        })
#
#    def queryset(self, request, queryset):
#        if self.value() == '1':
#            return queryset.filter(completed__isnull=False)
#        if self.value() == '2':
#            return queryset
#        return queryset.filter(completed__isnull=True)
#
#
#class SprintListFilter(admin.SimpleListFilter):
#    title = "Sprint"
#    parameter_name='sprint'
#
#    def lookups(self, request, model_admin):
#        return (
#            ('0', 'Current'),
#            ('1', utils.get_sprint_date(1).strftime('%b %d')),
#            ('2', utils.get_sprint_date(2).strftime('%b %d')),
#            ('3', utils.get_sprint_date(3).strftime('%b %d'))
#        )
#
#    def queryset(self, request, queryset):
#        try:
#            value = int(self.value())
#        except (ValueError, TypeError):
#            value = None
#        if value is None:
#            return queryset
#        task_sprints = utils.calculate_sprints()
#        task_ids = [t.id for t, s in task_sprints.iteritems() if s == value]
#        return queryset.filter(pk__in=task_ids)
#
#class TaskAdmin(OrderableAdmin):
#    list_display = ['_description', 'project', 'team', '_sprint', 'effort', 'deadline', 'completed']
#    list_editable = ['effort', 'completed']
#    list_filter = ['team', CompletedListFilter, SprintListFilter]
#
#    def _description(self, obj):
#        return obj.description.split('\n')[0]
#    _description.short_description = 'Description'
#
#    def _sprint(self, obj):
#        if obj.sprint == 0:
#            return 'Current'
#        if obj.sprint is None:
#            return '---'
#        return utils.get_sprint_date(obj.sprint).strftime('%b %d')
#    _sprint.short_description = 'Sprint'
#
#
#class ProjectAdmin(admin.ModelAdmin):
#    list_display = ['name', 'client']
#    list_filter = ['client']
#
#class ProjectInline(admin.TabularInline):
#    model = models.Project
#
#class ClientAdmin(admin.ModelAdmin):
#    inlines = [ProjectInline]
#
#class TeamAdmin(admin.ModelAdmin):
#    pass
#
#admin.site.register(models.Client, ClientAdmin)
#admin.site.register(models.Project, ProjectAdmin)
#admin.site.register(models.Task, TaskAdmin)
#admin.site.register(models.Team, TeamAdmin)
#admin.site.register(models.TeamStrengthAdjustment)
