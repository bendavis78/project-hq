from django.db.models import F
import sys

class OrderableModel(object):
    ordering_field = 'order'
    order_none_first = False

    class Meta:
        abstract = True

    def save(self):
        o = getattr(self, self.ordering_field)
        f = self.ordering_field
        Model = self.__class__
        if o:
            setattr(self, f, int(o))
            current = Model.objects.get(pk=self.pk)
            current_pos = getattr(current, f)
            if current_pos is None:
                if self.order_none_first == True:
                    current_pos = 0
                else:
                    current_pos = sys.maxint
            if current_pos > o:
                # when moving down, increment those between the move
                Model.objects.filter(**{('%s__lt' % f):current_pos, 
                        ('%s__gte' % f):o}).update(**{f:F(f)+1})
            elif getattr(current, f) < o:
                # when moving up, decrement those between the move
                Model.objects.filter(**{('%s__gt' % f):current_pos,
                        ('%s__lte' % f):o}).update(**{f:F(f)-1})

        super(OrderableModel, self).save()
