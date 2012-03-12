from django.db import models
import sys

class OrderableManager(models.Manager):
    _cleaning = False
    def clean_ordering(self):
        if self._cleaning:
            return
        self._cleaning = True
        objects = self.get_query_set()
        Model = objects.model
        f = Model.ordering_field
        objects = self.filter(**{'%s__isnull' % f:False})
        i = 1
        for object in objects.order_by(f):
            object.auto_order = False
            setattr(object, f, i)
            object.save()
            # if another class has overridden save to change the ordering
            # value, we just move on to the next one.
            if getattr(object, f) == i:
                i += 1
        self._cleaning = False

class OrderableModel(models.Model):
    ordering_field = 'order'
    order_none_first = False
    auto_order = True
    orderable = OrderableManager()
    _cleaning = False

    class Meta:
        abstract = True

    def save(self):
        if not self.auto_order:
            return super(OrderableModel, self).save()

        f = self.ordering_field
        o = getattr(self, f)
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
            objects = Model.objects.filter(**{'%s__isnull' % f:False})
            if current_pos > o:
                # when moving down, increment those between the move
                objects.filter(**{('%s__lt' % f):current_pos, 
                        ('%s__gte' % f):o}).update(**{f:models.F(f)+1})
            elif getattr(current, f) < o:
                # when moving up, decrement those between the move
                objects.filter(**{('%s__gt' % f):current_pos,
                        ('%s__lte' % f):o}).update(**{f:models.F(f)-1})
            
        return super(OrderableModel, self).save()

