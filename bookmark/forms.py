from django import forms

from bookmark.models import Restaurant


class VisitedForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = "__all__"


class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = "__all__"


class DeleteForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = {'name', 'business_id'}
