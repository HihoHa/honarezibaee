from django.db import models
from django.contrib.auth.models import User
from treebeard.ns_tree import NS_Node
from beauty.utils import m_view, ListFromStringRefiner, MobileViewRefiner
from image_cropping import ImageRatioField
from PIL import Image
from os import path
from django.core.files import File
import StringIO
import os
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.http import Http404


class ArticleTag(NS_Node):
    name = models.CharField(max_length=100, unique=True)
    node_order_by = ['name']

    def __unicode__(self):
        return self.name


class ArticleUrlCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class ArticleCategory(NS_Node):
    name = models.CharField(max_length=100)  # only persian letters
    multimedia_name = models.CharField(max_length=100, null=True, blank=True)
    node_order_by = ['name', ]
    menu_tags = models.ManyToManyField(ArticleTag, blank=True, null=True)
    ordering = models.FloatField(default=0)
    is_multimedia = models.BooleanField(default=False)
    url_name = models.ForeignKey(ArticleUrlCategory, null=True, blank=True)
    english_name = models.CharField(max_length=100, null=True, blank=True)

    def url_prefix(self):
        if self.get_root().url_name:
            return self.get_root().url_name.name
        else:
            return self.complete_url()

    def number_of_children(self):
        return len(self.get_children())

    def children(self):
        return self.get_children().order_by('ordering')

    def get_suggestion_root(self):
        if self.is_root() or self.is_child_of(self.get_root()):
            return self
        else:
            return self.get_ancestors()[1]

    def complete_url(self):
        if self.is_root():
            return self.name + u'\u202E'
        else:
            return self.get_parent().complete_url() + '/' + self.name + u'\u202E'

    def is_multimedia_type(self):
        if self.is_root():
            return self.is_multimedia
        else:
            return self.is_multimedia or self.get_parent().is_multimedia_type()

    def multimedia_root(self):
        if not self.is_multimedia_type():
            raise Exception('this category is not multimedia type')
        else:
            if self.is_multimedia:
                return self
            else:
                return self.get_parent().multimedia_root()

    @classmethod
    def from_url_string(cls, url):
        url = url.replace(u'\u202E', '/').replace(u'\u2069', '/')
        m_list = filter(None, url.split('/'))
        roots = cls.get_root_nodes()
        category = cls.get_from_list_by_name(roots, m_list[0])
        for i in range(1, len(m_list)):
            category = cls.get_from_list_by_name(category.get_children(), m_list[i])
            if not category:
                raise Http404("category doesn't exists: " + m_list[i])
        return category

    @classmethod
    def get_from_list_by_name(cls, m_list, name):
        for item in m_list:
            if item.name == name:
                return item
        return None

    def __unicode__(self):
        if self.is_root():
            return self.name
        else:
            return self.get_parent().__unicode__() + ' |> ' + self.name


class ArticleListManager(models.Manager):
    def get_queryset(self):
        return super(ArticleListManager, self).get_queryset().exclude(archive=True) \
            .exclude(do_not_publish_until__lte=datetime.utcnow())


class ArticleDetailManager(models.Manager):
    def get_queryset(self):
        return super(ArticleDetailManager, self).get_queryset().exclude(publish=False) \
            .exclude(do_not_publish_until__lte=datetime.utcnow())


@m_view(attribute_names=['content'], mobile_names=['m_content'], refiner_classes=[MobileViewRefiner])
class Article(models.Model):
    title = models.CharField(max_length=200)  # , unique_for_month=True)
    content = models.TextField()
    short_description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(ArticleTag, null=True, blank=True)
    category = models.ManyToManyField(ArticleCategory)
    main_category = models.ForeignKey(ArticleCategory, related_name='main_articles', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='article_avatar/', default='no-picture.jpg')
    cropping = ImageRatioField('image', '500x360')
    avatar_test_cropping = ImageRatioField('image', '250x180')
    small_test_cropping = ImageRatioField('image', '100x72')
    publish = models.BooleanField(default=False)
    archive = models.BooleanField(default=True)
    related_articles = models.ManyToManyField("self", symmetrical=False, null=True, blank=True)
    objects = models.Manager()
    non_archived_objects = ArticleListManager()
    publishable_objects = ArticleDetailManager()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    citations = models.IntegerField(default=0)
    video = models.FileField(upload_to='video/', null=True, blank=True)
    do_not_publish_until = models.DateTimeField(null=True, blank=True)

    @property
    def all_tags(self):
        all_tags = []
        for tag in self.tags.all():
            all_tags += tag.get_ancestors()
            all_tags.append(tag)
        return list(set(all_tags))

    def first_category(self):
        if not self.main_category:
            self.main_category = self.category.first()
            self.save()
        return self.main_category

    @classmethod
    def m_get_by_tag(cls, tag):
        tag_node = ArticleTag.objects.get(name=tag)
        tag_tree = ArticleTag.get_tree(tag_node)
        return Article.non_archived_objects.filter(tags__in=tag_tree)

    @classmethod
    def get_by_category(cls, category):
        category_tree = ArticleCategory.get_tree(category)
        return Article.non_archived_objects.filter(category__in=category_tree).distinct()

    def get_suggestion_query(self):
        # return Article.objects.all()
        category = self.first_category()
        if category is None:
            return None
        suggestion_root = category.get_suggestion_root()
        return Article.get_by_category(suggestion_root).exclude(pk=self.pk).distinct()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Article, self).save(force_insert, force_update, using,
                                  update_fields)
        self.avatar_test_cropping = self.cropping
        self.small_test_cropping = self.cropping
        super(Article, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.title

    def update_related_articles(self):
        how_many = 5 - self._num_of_related_articles
        if how_many > 0 and self.get_suggestion_query() is not None:
            for article in self.get_suggestion_query().filter(
                    created_at__gte=self.created_at - timedelta(days=45)).filter(
                    created_at__lte=self.created_at + timedelta(days=45)).exclude(pk=self.pk).distinct().order_by('citations')[:how_many]:
                self.related_articles.add(article)
        else:
            pass


@receiver(m2m_changed, sender=Article.related_articles.through, dispatch_uid="update_citations")
def my_handler(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_remove':
        for article in Article.objects.filter(pk__in=pk_set):
            article.citations -= 1
            article.save()
    if action == 'post_add':
        for article in Article.objects.filter(pk__in=pk_set):
            article.citations += 1
            article.save()


def update_handler(sender, instance, action, *args, **kwargs):
    if action == 'post_clear':
        instance.update_related_articles()

#
# @receiver(pre_save, sender=Article, weak=False, dispatch_uid="want_pre_num_of_related")
# def hold_num_of_related(sender, instance, **kargs):
#     if instance.pk:
#         instance._num_of_related_articles = instance.category.all().count()
#     else:
#         instance._num_of_related_articles = 0


@receiver(post_save, sender=Article, weak=False, dispatch_uid="post_save_update")
def update_related(sender, instance, **kwargs):
    m2m_changed.connect(update_handler, sender=Article.related_articles.through, weak=False)#, dispatch_uid='post_save_m2m_update')


class SlideShow(models.Model):
    article = models.OneToOneField(Article)
    image = models.ImageField(null=True, blank=True)
    cropping = ImageRatioField('image', '500x360')
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.article.__unicode__()


class AdBannerManager(models.Manager):
    def get_queryset(self):
        return super(AdBannerManager, self).get_queryset().filter(publish=True)


class AdvertisementBanner(models.Model):
    name = models.CharField(max_length=200, default='banner')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    banner = models.ImageField()
    link = models.URLField()
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    publish = models.BooleanField(default=False)
    objects = models.Manager()
    publishable = AdBannerManager()

    def __unicode__(self):
        return str(self.link)

    def redirect_link(self):
        return reverse('ad_view', kwargs={'banner_pk': self.pk})