from django import forms

from bookmark.models import Restaurant


class VisitedForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = Restaurant
        fields = "__all__"


class BookmarkForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = Restaurant
        fields = "__all__"


class DeleteForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = Restaurant
        fields = {'business_id'}


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=200)
