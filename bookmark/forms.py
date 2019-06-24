from django import forms

from bookmark.models import *


class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = {'business_id', 'name', 'rating', 'review_count', 'price', 'phone', 'image_url', 'yelp_url'}


class CategoryForm(forms.Form):
    categories = forms.CharField(max_length=200)


class DeleteForm(forms.Form):
    name = forms.CharField(max_length=50)
    location_id = forms.CharField(max_length=10)
    categories = forms.CharField(max_length=200)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=200)


class SortByForm(forms.Form):
    sort_by = forms.CharField(max_length=20)


class VisitedForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = Restaurant
        fields = "__all__"
