import ast
import datetime
from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView

from bookmark.forms import *
from bookmark.models import *


class SaveView(FormView):
    def post(self, request, *args, **kwargs):
        # Process restaurant, category, and location forms
        restaurant_form = RestaurantForm(request.POST, prefix='restaurant')
        category_form = CategoryForm(request.POST, prefix='category')
        location_form = LocationForm(request.POST, prefix='location')
        url = request.get_full_path().split()[0]

        if restaurant_form.is_valid() and category_form.is_valid() and location_form.is_valid():
            # Set up parameters to validators
            location = self.get_location(location_form)
            restaurant = self.get_restaurant(restaurant_form)
            categories = self.get_categories(category_form)

            self.location_form_valid(location)
            self.restaurant_form_valid(restaurant, location, url)
            self.category_form_valid(categories, restaurant)
        else:
            if url == '/add-to-visited-from-bookmarks':
                business_id = request.POST.get('business_id')
                name = request.POST.get('name')
            else:
                business_id = restaurant_form['business_id'].value()
                name = restaurant_form['name'].value()

            # Attempt retrieval of object from Restaurant relation
            try:
                restaurant = Restaurant.objects.filter(pk=business_id).get()
                if Bookmarks.objects.filter(restaurant=restaurant).exists() and url == '/add-to-bookmarks':
                    # Object is already in bookmarks, display warning message
                    messages.warning(self.request, f'{name} is already in your bookmarks!')
                elif Bookmarks.objects.filter(restaurant=restaurant).exists() \
                        and (url == '/add-to-visited' or url == '/add-to-visited-from-bookmarks'):
                    # Object exists in bookmarks, but we want to delete from bookmarks and add to visited
                    Bookmarks.objects.filter(restaurant=restaurant).delete()
                    Visited.objects.create_visited(restaurant=restaurant).save()
                    messages.success(self.request, f"Added {name} to your visited list!")
                elif Visited.objects.filter(restaurant=restaurant).exists():
                    # Object is already in visited, display warning message
                    messages.warning(self.request, f'{name} is already in your visited list!')
                else:
                    # Display error message, look into problem
                    messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
            except exceptions.ObjectDoesNotExist:
                # Display error message, look into problem
                messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')

        return redirect(self.request.META.get('HTTP_REFERER'))

    def restaurant_form_valid(self, restaurant, location, url):
        # Save restaurant and create bookmark if not already in Restaurant relation
        if not Restaurant.objects.filter(pk=restaurant['business_id']).exists():
            restaurant['location'] = Location.objects.get(address=location['address'],
                                                          postal_code=location['postal_code'])
            res = Restaurant.objects.create_restaurant(restaurant)

            if url == '/add-to-bookmarks':
                Bookmarks.objects.create_bookmark(date=datetime.datetime.now(), restaurant=res).save()
                messages.success(self.request, "Added {name} to bookmarks!".format(name=restaurant['name']))
            elif url == '/add-to-visited':
                Visited.objects.create_visited(restaurant=res).save()
                messages.success(self.request, "Added {name} to your visited list!".format(name=restaurant['name']))

    @staticmethod
    def location_form_valid(location):
        # Save location if not already in Location relation
        if not Location.objects.filter(address=location['address'], postal_code=location['postal_code']).exists():
            Location.objects.create_location(location)

    @staticmethod
    def category_form_valid(categories, restaurant):
        for category in categories:
            # Save category if not already in Category relation
            if not Category.objects.filter(title=category['title'], alias=category['alias']).exists():
                Category.objects.create_category(title=category['title'], alias=category['alias']).save()

            # Save (business_id, category) pair if not already in RestaurantHasCategory relation
            res = Restaurant.objects.filter(pk=restaurant['business_id'])[0]
            category = Category.objects.filter(title=category['title'], alias=category['alias'])[0]
            if not RestaurantHasCategory.objects.filter(restaurant=res, category=category).exists():
                RestaurantHasCategory.objects.create_object(res, category).save()

    @staticmethod
    def get_restaurant(restaurant_form):
        return {'save': restaurant_form.cleaned_data.get('save'),
                'business_id': restaurant_form.cleaned_data.get('business_id'),
                'name': restaurant_form.cleaned_data.get('name'),
                'rating': restaurant_form.cleaned_data.get('rating'),
                'review_count': restaurant_form.cleaned_data.get('review_count'),
                'price': restaurant_form.cleaned_data.get('price'),
                'phone': restaurant_form.cleaned_data.get('phone'),
                'image_url': restaurant_form.cleaned_data.get('image_url'),
                'yelp_url': restaurant_form.cleaned_data.get('yelp_url')}

    @staticmethod
    def get_location(location_form):
        return {'address': location_form.cleaned_data.get('address'),
                'city': location_form.cleaned_data.get('city'),
                'province': location_form.cleaned_data.get('province'),
                'country': location_form.cleaned_data.get('country'),
                'postal_code': location_form.cleaned_data.get('postal_code'),
                'latitude': location_form.cleaned_data.get('latitude'),
                'longitude': location_form.cleaned_data.get('longitude')}

    @staticmethod
    def get_categories(category_form):
        return ast.literal_eval(category_form.cleaned_data.get('categories'))
