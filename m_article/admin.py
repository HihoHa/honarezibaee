from django import forms
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.core.exceptions import ObjectDoesNotExist
from m_article.models import Article, ArticleTag, ArticleCategory, SlideShow
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from m_article.utils import cleaner, localize
from multiupload.fields import MultiFileField
from django.conf import settings
import os
from urlparse import urljoin
from datetime import datetime, timedelta
from image_cropping import ImageCroppingMixin

MEDIA_ROOT, MEDIA_URL = settings.MEDIA_ROOT, settings.MEDIA_URL


class TagAdmin(TreeAdmin):
    form = movenodeform_factory(ArticleTag)
    list_filter = ('name',)


class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(ArticleCategory)
    list_filter = ('name',)


class ArticleAdminForm(forms.ModelForm):
    multifile = MultiFileField(required=False, max_file_size=5*1024*1024)
    download_images = forms.BooleanField(required=False)
    clean_style = forms.BooleanField(required=False)
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
        if clean:
            content = data.get('content')
            data['content'] = cleaner.clean_html(content)
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


class ArticleAdmin(ImageCroppingMixin):  # , SummernoteModelAdmin):
    form = ArticleAdminForm
    change_form_tamplate = 'm_article/admin/change_form.html'

    fields = ('title', 'content', 'clean_style', 'multifile', 'tags', 'category',
              'created_at', 'download_images', 'cropping', 'video',
              'image', 'small_image', 'related_articles', 'publish',
              'archive', 'likes', 'dislikes', 'views', 'citations', 'do_not_publish_until')
    readonly_fields = ('created_at', 'likes', 'dislikes', 'views', 'small_image', 'citations')
    list_filter = ('category', 'tags', 'publish', 'archive')
    list_display = ('title', 'publish', 'archive', 'created_at')
    list_editable = ('publish', 'archive')
    search_fields = ('title',)
    filter_horizontal = ('tags', 'category', 'related_articles')
    save_as = True

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

admin.site.register(ArticleTag, TagAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategory, CategoryAdmin)
admin.site.register(SlideShow, SlideShowAdmin)