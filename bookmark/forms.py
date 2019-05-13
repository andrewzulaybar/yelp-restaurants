from django import forms

from bookmark.models import Restaurant


class VisitedForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = "__all__"
