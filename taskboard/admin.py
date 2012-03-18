from django.contrib import admin
from taskboard import models

class TeamAdmin(admin.ModelAdmin):
    exclude = ['permissions']

admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.TeamStrengthAdjustment)
