from django import forms
from history.forms import CommentForm
from taskboard import models

def optional(choices):
    return (('',''),) + choices



class CommentForm(CommentForm):
    comment = forms.CharField(widget=forms.Textarea,
            required=False)

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = models.Task
        widgets = {
            'ticket': forms.HiddenInput
        }
