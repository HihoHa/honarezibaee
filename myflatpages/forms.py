from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import MyFlatPage
from django.contrib.flatpages.admin import FlatpageForm


class MyFlatpageForm(FlatpageForm):
    description = forms.CharField(widget=CKEditorWidget, required=False)
    content = forms.CharField(widget=CKEditorWidget, required=False)

    class Meta:
        model = MyFlatPage