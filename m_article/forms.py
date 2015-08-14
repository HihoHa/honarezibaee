from django import forms

class CommentForm(forms.Form):
    comment = forms.CharField(label = "comment", widget=forms.Textarea(attrs={'rows':'3'}))