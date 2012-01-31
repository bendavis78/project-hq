from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Project(models.Model):
    client = models.ForeignKey(Client, related_name='projects')
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '[%s] %s' % (self.client.name, self.name)

    class Meta:
        ordering = ['client', 'name']

class ProjectLink(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50)
    url = models.URLField()
