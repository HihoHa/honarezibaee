from django import forms
from .models import JobContent


class JobSearchForm(forms.Form):
    keywords = forms.CharField(label='', required=False)
    name = forms.CharField(label='', required=False)
    page = forms.IntegerField(required=False,
                              widget=forms.TextInput(
                                  attrs={'style': 'display:none'}), label='')


class JobContentForm(forms.ModelFrom):
    class Meta:
        model = JobContent
        fields = '__all__'
