from django.contrib import admin
from taskboard import models

class TeamAdmin(admin.ModelAdmin):
    exclude = ['permissions']
    list_display = ['name', 'velocity']

class TeamStrengthAdmin(admin.ModelAdmin):
    list_display = ['team', 'start_date', 'end_date', 'percentage']

admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.TeamStrengthAdjustment, TeamStrengthAdmin)
