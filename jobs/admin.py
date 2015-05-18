from django.contrib import admin
from . import models
from django_summernote.admin import SummernoteModelAdmin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from django import forms
import logging

logger = logging.getLogger('django')


# Register your models here.
class JobAdmin(SummernoteModelAdmin):
    model = models.Job
    list_display = ('title','address')
    filter_horizontal = ('tags', 'category')
    save_as = True
    actions_on_top = True

class TagAdmin(TreeAdmin):
    form = movenodeform_factory(models.JobTag)
    list_filter = ('name',)
    save_as = True

# base_form = movenodeform_factory(models.JobCategory)

# class CategoryForm(base_form):
#     def clean(self):
#         data = super(CategoryForm, self).clean()
#         if self.instance and self.instance.get_depth() > 2:
#             raise forms.ValidationError('fuck')

class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(models.JobCategory)
    list_filter = ('name',)
        



admin.site.register(models.Job, JobAdmin)
admin.site.register(models.JobTag, TagAdmin)
admin.site.register(models.JobCategory, CategoryAdmin)