from django import forms
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.core.exceptions import ObjectDoesNotExist
from m_article.models import Article, ArticleTag, ArticleCategory, SlideShow, ArticleUrlCategory, AdvertisementBanner
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from m_article.utils import cleaner, localize, edit_image_attr, with_new_line
from multiupload.fields import MultiFileField
from django.conf import settings
import os
from urlparse import urljoin
from datetime import datetime, timedelta
from image_cropping import ImageCroppingMixin
from ckeditor.widgets import CKEditorWidget
from django.core.urlresolvers import reverse
from django.contrib.admin.widgets import FilteredSelectMultiple
import sys

MEDIA_ROOT, MEDIA_URL = settings.MEDIA_ROOT, settings.MEDIA_URL


class TagAdmin(TreeAdmin):
    form = movenodeform_factory(ArticleTag)
    list_filter = ('name',)
    list_per_page = 400


class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(ArticleCategory)
    list_filter = ('name',)


import logging
log = logging.getLogger(__name__)
# convert the errors to text
from django.utils.encoding import force_text


class ArticleAdminForm(forms.ModelForm):

    def is_valid(self):

        print >>sys.stderr, '********self.errors: ' + force_text(self.errors)
        return super(ArticleAdminForm, self).is_valid()

    def __init__(self, *args, **kwargs):
        print >>sys.stderr, 'Goodbye, cruel world!'
        super(ArticleAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            queryset = self.instance.get_suggestion_query()
        else:
            queryset = Article.objects.all()

        self.fields['related_articles'] = forms.ModelMultipleChoiceField(required=False,
            queryset=queryset, widget=FilteredSelectMultiple('Related Articles', False, attrs={'style': 'direction: rtl;'}))

    multifile = MultiFileField(required=False, max_file_size=5*1024*1024)
    download_images = forms.BooleanField(required=False)
    clean_style = forms.BooleanField(required=False)
    content = forms.CharField(widget=CKEditorWidget())
    title = forms.CharField(widget=forms.TextInput(attrs={'style': 'direction: rtl; width: 600px;'}))
    short_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'style': 'direction: rtl; width: 600px;'}))
    category = forms.ModelMultipleChoiceField(queryset=ArticleCategory.objects.all(), widget=FilteredSelectMultiple("Category", False, attrs={'style': 'direction: rtl;'}))
    tag = forms.ModelMultipleChoiceField(required=False, queryset=ArticleTag.objects.all(), widget=FilteredSelectMultiple("Category", False, attrs={'style': 'direction: rtl;'}))


    # update_related_articles = forms.BooleanField(required=False)

    class Meta:
        model = Article


    def clean_video(self):
        video = self.cleaned_data['video']
        if video and video.name.split('.')[-1] not in ['mp4', 'flv']:
            raise forms.ValidationError('only mp4 or flv files')
        return video

    # download the images if neccessary
    def clean(self):
        data = super(ArticleAdminForm, self).clean()
        if data.get('download_images'):
            data['content'] = localize(data['content'])
        publish = data.get('publish')
        archive = data.get('archive')
        clean = data.get('clean_style')
        content = data.get('content')
        if clean:
            content = cleaner.clean_html(content)
        if 'title' in data and 'category' in data:
            data['content'] = edit_image_attr(content, url=reverse('article_view', kwargs={'article_title': data['title'], 'category_name': data['category'].all().first().url_prefix()}), alt=data['title'])
        if 'content' in data:
            data['content'] = with_new_line(data['content'])
        if not publish and not archive:
            raise forms.ValidationError("A non publishable article should be archived.")
        return data

    def save(self, commit=True):
        """ikhtar!!! doesnt support commit=False!!!"""
        # todo

        a = super(ArticleAdminForm, self).save(commit=False)

        try:
            old_a = Article.objects.get(pk=a.pk)
        except Article.DoesNotExist:
            old_a = None

        a.save()
        if not old_a:
            a.update_small_image()
        elif not old_a.small_image or old_a.image != a.image:
            old_a.small_image.delete()
            a.update_small_image()

        for image in self.cleaned_data['multifile']:
            path = os.path.join(MEDIA_ROOT, a.title, image.name)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))  # light todo: check for concurrent access: http://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
            with open(path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
                a.content = a.content + '<p class="text-center"><strong>%s</strong></p>' % a.title +'<a href="/"><img src="%s" class="img-responsive center-block"></a>' % urljoin(MEDIA_URL,
                a.title + '/' + image.name)
        if commit:
            a.save()
        return a


class ArticleAdmin(ImageCroppingMixin, admin.ModelAdmin):  # , SummernoteModelAdmin):
    form = ArticleAdminForm
    # change_form_tamplate = 'm_article/admin/change_form.html'

    fields = ( 'title', 'short_description', 'content', 'clean_style', 'multifile',
              'tags', 'category',
              'created_at',
              'download_images',
              'cropping', 'video',
              'image', 'small_image', 'related_articles', 'publish',
              'archive', 'likes', 'dislikes', 'views', 'citations', 'do_not_publish_until')
    readonly_fields = ('created_at', 'likes', 'dislikes', 'views', 'small_image', 'citations')
    list_filter = ('category', 'tags', 'publish', 'archive')
    list_display = ('title', 'publish', 'archive', 'created_at', 'likes', 'dislikes', 'first_category', 'views')
    ordering = ('-created_at',)
    list_editable = ('publish', 'archive')
    search_fields = ('title',)
    filter_horizontal = ('tags', 'category', 'related_articles')
    save_as = False

    def get_search_results(self, request, queryset, search_term):  # for search on articles page
        queryset, use_distinct = super(ArticleAdmin, self).get_search_results(request, queryset, search_term)
        try:
            search_node = ArticleTag.objects.get(name=search_term)
        except ObjectDoesNotExist:
            pass
        else:
            queryset |= self.model.objects.filter(tags__in=ArticleTag.get_tree(search_node))
        return queryset, use_distinct

    def get_changelist_form(self, request, **kwargs):
        return ArticleAdminForm


class SlideShowForm(forms.ModelForm):
    class Meta:
        model = SlideShow
        fields = '__all__'


class SlideShowAdmin(SummernoteModelAdmin):
    form = SlideShowForm


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'views', 'clicks')

from django.contrib.flatpages.models import FlatPage
 
# Note: we are renaming the original Admin and Form as we import them!
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld
from django.contrib.flatpages.admin import FlatpageForm as FlatpageFormOld


class FlatpageForm(FlatpageFormOld):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage  # this is not automatically inherited from FlatpageFormOld
 
 
class FlatPageAdmin(FlatPageAdminOld):
    form = FlatpageForm
 
 
# We have to unregister the normal admin, and then reregister ours
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

admin.site.register(ArticleTag, TagAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategory, CategoryAdmin)
admin.site.register(SlideShow, SlideShowAdmin)
admin.site.register(ArticleUrlCategory)
admin.site.register(AdvertisementBanner, BannerAdmin)