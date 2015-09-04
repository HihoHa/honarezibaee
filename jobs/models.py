from django.db import models
from beauty.utils import m_view, ListFromStringRefiner, MobileViewRefiner
from treebeard.ns_tree import NS_Node
# from location_field.models.plain import PlainLocationField
from geoposition.fields import GeopositionField
from django.core.exceptions import ValidationError
import logging
from decimal import getcontext as gc
from django.contrib.auth.models import User

gc.prec = 16

logger = logging.getLogger('django')


class JobTag(NS_Node):
    name = models.CharField(max_length=200, unique=True)
    node_order_by = ['name']

    def __unicode__(self):
        return self.name


class JobCategory(NS_Node):
    name = models.CharField(max_length=200, unique=True)
    node_order_by = ['name']

    def clean(self):
        if self.get_depth() > 2:
            raise ValidationError('Job categories must be of length'
                                  'of at most 2')

    def __unicode__(self):
        return self.name


class JobContent(models.Model):
    title = models.CharField(max_length=1000, null=True, blank=True)
    description = models.TextFild(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    location = GeopositionField(null=True, blank=True)


@m_view(attribute_names=['description', 'address', 'title'],
        mobile_names=['m_description', 'm_address', 'word_list'],
        refiner_classes=[MobileViewRefiner, MobileViewRefiner,
                         ListFromStringRefiner])
class Job(models.Model):
    author = models.ForiegnKey(User)
    tags = models.ManyToManyField(JobTag, null=True, blank=True)
    category = models.ManyToManyField(JobCategory, blank=True, null=True)
    content = models.ForiegnKey(JobContent, null=True)

    @property
    def ID(self):
        return 'ID' + str(self.id + 1000).zfill(5)

    @property
    def title(self):
        if self.content:
            return self.content.title
        else:
            return None

    @property
    def description(self):
        if self.content:
            return self.content.description
        else:
            return None

    @property
    def address(self):
        if self.content:
            return self.content.address
        else:
            return None

    @property
    def location(self):
        if self.content:
            return self.content.location
        else:
            return None

    @property
    def email_address(self):
        if self.content:
            return self.content.email_address
        else:
            return None

    def long(self):
        if self.content:
            return str(self.content.location.longitude)
        else:
            return None

    def lat(self):
        if self.content:
            return str(self.content.location.latitude)
        else:
            return None

    def __unicode__(self):
        return self.ID

    @classmethod
    def get_by_category(cls, category_name):
        category_node = JobCategory.objects.get(name=category_name)
        category_tree = JobCategory.get_tree(category_node)
        return Job.objects.filter(category__in=category_tree)

    @classmethod
    def get_by_tag(cls, tag_pk):
        tag_node = JobTag.objects.get(pk=tag_pk)
        tag_tree = JobTag.get_tree(tag_node)
        return Job.objects.filter(tags__in=tag_tree)


class JobChange(models.Model):
    job = models.ForiegnKey(Job, unique=True, null=True)
    status = models.CharField(max_length=4, choices=('w', 'r'), deafult='w')
    modified = models.DateTimeField(auto_now=True)
    content = models.ForiegnKey(JobContent, null=True)
    message = models.CharField(max_length=1000, null=True)
