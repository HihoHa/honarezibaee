from django import forms

class JobSearchForm(forms.Form):
    keywords = forms.CharField(label='', required=False)
    name = forms.CharField(label='', required=False)
    page = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style':'display:none'}), label='')

    # def clean(self):
        
    # address = forms.CharField(label='address', required=False)
    # title = forms.CharField(label='title', required=False)

    # def __init__(self, *args, **kwargs):
    #     if 'category_names' in kwargs:
    #         category_names = kwargs['category_names']
    #         del kwargs['category_names']
    #     else:
    #         category_names = []
    #     super(JobSearchForm, self).__init__(*args, **kwargs)
    #     for name in category_names:
    #         self.fields['extra_%s' % name] = forms.BooleanField(label=name, required=False)#should i set required = False?
            
    # def extra_fields(self):
    #     for name, value in self.cleaned_data.items():
    #         if name.startswith('extra_'):
    #             yield (self.fields[name].label, value)