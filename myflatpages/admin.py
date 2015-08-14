from django.contrib import admin

from django.contrib.flatpages.models import FlatPage
from .models import MyFlatPage

from django.contrib.flatpages.admin import FlatPageAdmin
from .forms import MyFlatpageForm

from django.utils.translation import ugettext_lazy as _


class MyFlatpageAdmin(FlatPageAdmin):
    form = MyFlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites', 'description')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
admin.site.register(MyFlatPage, MyFlatpageAdmin)
