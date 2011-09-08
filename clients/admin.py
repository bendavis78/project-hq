from django.contrib import admin
from clients import models

class ProjectLinkInline(admin.TabularInline):
    model =  models.ProjectLink
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectLinkInline]

admin.site.register(models.Client)
admin.site.register(models.Project, ProjectAdmin)
