import ast
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView

from bookmark.forms import DeleteForm
from bookmark.models import *


class DeleteView(FormView):
    form_class = DeleteForm

    def post(self, request, *args, **kwargs):
        delete_form = DeleteForm(request.POST)

        if delete_form.is_valid():
            self.form_valid(delete_form)
        else:
            self.form_invalid(delete_form)

        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_valid(self, form):
        business_id = form.cleaned_data.get('business_id')
        name = form.cleaned_data.get('name')

        # Retrieve restaurant, location, and category objects related to business_id
        restaurant = Restaurant.objects.get(business_id=business_id)
        location = Location.objects.get(restaurant__in=Restaurant.objects.filter(business_id=business_id))
        categories = Category.objects.filter(
            restauranthascategory__in=RestaurantHasCategory.objects.filter(restaurant_id=business_id)
        )

        # Delete category from database if no other restaurants are in this category
        for category in categories:
            restaurants_in_category = RestaurantHasCategory.objects.filter(category=category)
            if len(restaurants_in_category) == 1:
                category.delete()

        # Delete location from database if no other restaurants share this location
        # NOTE: deletion of location also deletes restaurant by foreign key constraint
        restaurants_at_location = Restaurant.objects.filter(location=location)
        location.delete() if len(restaurants_at_location) == 1 else restaurant.delete()

        messages.success(self.request, f'Successfully deleted {name}!')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        # Display error message and refresh page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect(self.request.META.get('HTTP_REFERER'))
