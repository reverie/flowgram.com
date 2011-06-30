"""Abstract base models to be imported in models.py"""

from django.conf import settings
from django.db import models

##################################################################
######              ModelWithCaching
##################################################################

from django.core.cache import cache

ModelBase = type(models.Model)

CACHE_PREFIX = settings.CACHE_MIDDLEWARE_KEY_PREFIX
CACHE_EXPIRE = 30

def cache_key(model, pk):
    # This function was copied from somewhere I think
    return ('%s:%s:%s' % (CACHE_PREFIX, model._meta.db_table, pk)).replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '')[:250]

def model_key(model):
    return cache_key(model, model.pk)[:247] + ":mk"

from flowgram.core import log

class RowCacheManager(models.Manager):
    """Manager for caching single-row queries. To make invalidation possible,
    we use an extra layer of indirection. The query arguments are used as a
    cache key, whose stored value is the (unique) cache key pointing to the
    object. When a model using RowCacheManager is saved, this unique cache
    should be invalidated."""

    def get(self, *args, **kwargs):
        # TODO: skip the layer of indirection if 'kwargs' contains id or pk?
        
        #log.debug("RowCacheManager get")

        id_list = []
        
        keys = kwargs.keys()
        keys.sort()
        
        for key in keys:
            try:
                id_list.append(str(kwargs[key].id))
            except:
                id_list.append(str(kwargs[key]))

        id = "".join(id_list)

        #log.debug("id = " + str(id))

        pointer_key = cache_key(self.model, id)
        #log.debug("pointer_key = " + str(pointer_key))
        
        mk = cache.get(pointer_key)
        
        if mk is not None:
            #log.debug("mk = " + str(mk))
            
            model = cache.get(mk)
            if model is not None:
                return model

        # One of the cache queries missed, so we have to get the object from the database:
        model = super(RowCacheManager, self).get(*args, **kwargs)
        
        if not mk:
            mk = model_key(model)
            #log.debug("SET mk = " + str(mk))
            
            cache.set(pointer_key, mk, CACHE_EXPIRE)
            
        cache.set(mk, model, CACHE_EXPIRE) # you can use 'add' instead of 'set' here
        return model
    
class MetaCaching(ModelBase):
    """Sets ``objects'' on any model that inherits from ModelWithCaching to
    be a RowCacheManager."""
    def __new__(*args, **kwargs):
        new_class = ModelBase.__new__(*args, **kwargs)
        new_manager = RowCacheManager()
        new_manager.contribute_to_class(new_class, 'objects')
        new_class._default_manager = new_manager
        return new_class

class ModelWithCaching(models.Model):
    def save(self, *args, **kwargs):
        super(ModelWithCaching, self).save()
        
        if kwargs.pop('invalidate_cache', True):
            mk = model_key(self)
            cache.delete(mk)

    class Meta:
        abstract = True
    __metaclass__ = MetaCaching

##################################################################
######              ModelWithRandomID                      
##################################################################
    
from flowgram.core.securerandom import secure_random_id

class ModelWithRandomID(models.Model):
    id = models.CharField(primary_key=True, max_length=settings.ID_FIELD_LENGTH)
    def save(self):
        if not self.id:
            self.id = secure_random_id(settings.ID_ACTUAL_LENGTH)
        super(ModelWithRandomID, self).save()
    class Meta:
        abstract = True
        
