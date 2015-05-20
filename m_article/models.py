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
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse


SIZE = 205, 205  # size for thumbnails of article


class ArticleTag(NS_Node):
    name = models.CharField(max_length=100, unique=True)
    node_order_by = ['name']

    def __unicode__(self):
        return self.name


class ArticleCategory(NS_Node):
    name = models.CharField(max_length=100, unique=True)
    node_order_by = ['name', ]
    menu_tags = models.ManyToManyField(ArticleTag, blank=True, null=True)
    ordering = models.IntegerField(default=0)

    def children(self):
        return self.get_children().order_by('ordering')

    def get_suggestion_root(self):
        if self.is_root() or self.is_child_of(self.get_root()):
            return self
        else:
            return self.get_ancestors()[1]


    def __unicode__(self):
        return self.name


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
    category = models.ManyToManyField(ArticleCategory, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='article_avatar/', default='no-picture.png')
    cropping = ImageRatioField('image', '500x360')
    small_cropping = ImageRatioField('image', '150x100')
    small_image = models.ImageField(upload_to='article_avatar/', null=True, blank=True)
    publish = models.BooleanField(default=True)
    archive = models.BooleanField(default=False)
    related_articles = models.ManyToManyField("self", null=True, blank=True)
    objects = models.Manager()
    non_archived_objects = ArticleListManager()
    publishable_objects = ArticleDetailManager()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    citations = models.IntegerField(default=0)
    video = models.FileField(upload_to='video/', null=True, blank=True)
    do_not_publish_until = models.DateTimeField(null=True, blank=True)

    @classmethod
    def m_get_by_tag(cls, tag):
        tag_node = ArticleTag.objects.get(name=tag)
        tag_tree = ArticleTag.get_tree(tag_node)
        return Article.non_archived_objects.filter(tags__in=tag_tree)

    @classmethod
    def get_by_category(cls, category_name):
        category_node = ArticleCategory.objects.get(name=category_name)
        category_tree = ArticleCategory.get_tree(category_node)
        return Article.non_archived_objects.filter(category__in=category_tree).distinct()

    def get_suggestion_query(self):
        category = self.category.all().first()
        if category is None:
            return None
        suggestion_root = category.get_suggestion_root()
        return Article.get_by_category(suggestion_root)

    def update_small_image(self):
        """ikhtar!!! doesnt save the model!!!"""
        image = Image.open(self.image.path)
        image.thumbnail(SIZE, Image.ANTIALIAS)

        thumb_io = StringIO.StringIO()
        image_path = os.path.splitext(self.image.path)
        image.save(thumb_io, format='JPEG', quality=85)

        image_path = image_path[0] + '_small' + image_path[1]

        self.small_image.save(image_path, File(thumb_io), save=False)

    def __unicode__(self):
        return self.title

    def update_related_articles(self):
        how_many = 5 - self.related_articles.count()
        if how_many > 0 and self.get_suggestion_query() is not None:
            for article in self.get_suggestion_query().filter(
                    created_at__gte=self.created_at - timedelta(days=45)).filter(
                    created_at__lte=self.created_at + timedelta(days=45)).exclude(pk=self.pk).exclude().order_by('citations')[:how_many]:
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


class FirstPageLinks(models.Model):
    category = models.ForeignKey(ArticleCategory)
    tag = models.ForeignKey(ArticleTag, null=True, blank=True)