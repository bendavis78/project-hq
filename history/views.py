from history import forms
from history import models
from django import http

class CommentViewMixin(object):

    def __init__(self, *args, **kwargs):
        super(CommentViewMixin, self).__init__(*args, **kwargs)
        if not getattr(self, 'comment_form_class'):
            self.comment_form_class = forms.CommentForm

    def get(self, *args, **kwargs):
        self.comment_form = self.comment_form_class()
        return super(CommentViewMixin, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.comment_form = self.comment_form_class(self.request.POST)
        if self.comment_form.is_valid():
            data = self.comment_form.cleaned_data
            if all(v == '' for v in data.values()):
                return super(CommentViewMixin, self).get(*args, **kwargs)
            obj = self.get_object()
            event = self.save_comment_form(self.comment_form, obj)
            obj.log_changes(event)
            obj.save()
            return http.HttpResponseRedirect('.')

    def save_comment_form(self, comment_form, obj):
        data = comment_form.cleaned_data
        comment = None
        event = models.Event(object=obj, user_id=self.request.user.id)
        event.save()
        if data['comment']:
            comment = models.Comment(event=event, message=data['comment'])
            comment.save()
        return event
        
    def get_context_data(self, **kwargs):
        context = super(CommentViewMixin, self).get_context_data(**kwargs)
        context.update({
            'comment_form': self.comment_form,
        })
        return context

class HistoryUpdateMixin(object):
    def form_valid(self, form):
        obj = form.save(commit=False)
        event = models.Event(object=obj, user_id=self.request.user.id)
        event.save()
        obj.log_changes(event)
        return super(HistoryUpdateMixin, self).form_valid(form)
