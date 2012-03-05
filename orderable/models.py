from django.db.models import F

class OrderableModel(object):
    class Meta:
        abstract = True

    def save(self):
        o = getattr(self, self.ordering_field)
        f = self.ordering_field
        Model = self.__class__
        if o:
            setattr(self, f, int(o))
            current = Model.objects.get(pk=self.pk)
            if getattr(current, f) > o:
                # when moving down, increment those between the move
                Model.objects.filter(**{('%s__lt' % f):getattr(current, f), 
                        ('%s__gte' % f):o}).update(**{f:F(f)+1})
            elif getattr(current, f) < o:
                # when moving up, decrement those between the move
                Model.objects.filter(**{('%s__gt' % f):getattr(current, f),
                        ('%s__lte' % f):o}).update(**{f:F(f)-1})

        super(OrderableModel, self).save()
