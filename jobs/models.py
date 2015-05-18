from django.db import models
from beauty.utils import m_view, ListFromStringRefiner, MobileViewRefiner
from treebeard.ns_tree import NS_Node
# from location_field.models.plain import PlainLocationField
from geoposition.fields import GeopositionField
from django.core.exceptions import ValidationError
import logging
from decimal import getcontext as gc

gc.prec = 16

logger = logging.getLogger('django')

class JobTag(NS_Node):
    name = models.CharField(max_length=200, unique=True)
    node_order_by = ['name',]

    def __unicode__(self):
        return self.name

class JobCategory(NS_Node):
    name = models.CharField(max_length=200, unique=True)
    node_order_by = ['name',]

    def clean(self):
        if self.get_depth() > 2:
            raise ValidationError('Job categories must be of length of at most 2')

    def __unicode__(self):
        return self.name

#@m_view(attribute_name='address', mobile_name='m_address')
#@m_view(attribute_name='title', mobile_name='word_list', refiner_class=ListFromStringRefiner)
@m_view(attribute_names=['description', 'address','title'], mobile_names = ['m_description', 'm_address', 'word_list'], refiner_classes=[MobileViewRefiner, MobileViewRefiner, ListFromStringRefiner])
class Job(models.Model):
    title = models.CharField(max_length=1000, unique=True)
    description = models.TextField()
    address = models.TextField()
    email_address = models.EmailField(null=True, blank=True)
    tags = models.ManyToManyField(JobTag, null=True, blank=True)
    category = models.ManyToManyField(JobCategory, blank=True, null=True)
    location = GeopositionField(null=True, blank=True)

    def long(self):
        return str(self.location.longitude)

    def lat(self):
        return str(self.location.latitude)

    def __unicode__(self):
        return self.title

    @classmethod
    def get_by_category(cls, category_name):
        category_node = JobCategory.objects.get(name=category_name)
        category_tree = JobCategory.get_tree(category_node)
        return Job.objects.filter(category__in=category_tree)

    def get_by_tag(cls, tag_pk):
        tag_node = JobTag.objects.get(pk=tag_pk)
        tag_tree = JobTag.get_tree(tag_node)
        return Job.objects.filter(tags__in=tag_tree)