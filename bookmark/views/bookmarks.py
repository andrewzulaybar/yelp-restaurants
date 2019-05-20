from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import BookmarkForm
from bookmark.models import Restaurant


class BookmarksMixin(object):
    model = Restaurant
    template_name = 'bookmark/bookmarks.html'
    context_object_name = 'restaurants'

    # Additional parameters
    params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}


class BookmarksListView(BookmarksMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(BookmarksListView, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)

        context[self.context_object_name] = bookmarks
        return context


class AddToBookmarksView(FormView):
    form_class = BookmarkForm

    def form_valid(self, form):
        # Save name and business_id
        name = form.cleaned_data.get('name')
        business_id = form.cleaned_data.get('business_id')

        # Attempt retrieval of object from database
        try:
            r = Restaurant.objects.filter(business_id=business_id).get()
            if r.bookmark:
                # Object is already in bookmarks, display warning message
                messages.warning(self.request, f'{name} is already in your bookmarks list!')
            else:
                # Object is in visited, display warning message
                messages.warning(self.request, f'{name} is in your visited list!')
        except exceptions.ObjectDoesNotExist:
            # Object does not yet exist, save to database and display success message
            form.save()
            messages.success(self.request, f'Added {name} to bookmarks!')

        # Redirect user to home page
        return redirect('bookmark-home')

    def form_invalid(self, form):
        # Display error message and redirect user to home page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect('bookmark-home')


class IsOpenNow(BookmarksMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(IsOpenNow, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Open Now'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                # If restaurant is open now, add to context
                try:
                    if r['hours'][0]['is_open_now']:
                        bookmarks.append(r)
                except KeyError:
                    pass

        context[self.context_object_name] = bookmarks
        return context


class SortByCuisine(BookmarksMixin, ListView):
    def sort_by_cuisine(self, elem):
        return elem['categories'][0]['title']

    def get_context_data(self, **kwargs):
        context = super(SortByCuisine, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Cuisine'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)

        # Sort alphabetically by first category title
        bookmarks.sort(key=self.sort_by_cuisine)

        context[self.context_object_name] = bookmarks
        return context


class SortByRating(BookmarksMixin, ListView):
    def sort_by_rating(self, elem):
        return elem['rating']

    def get_context_data(self, **kwargs):
        context = super(SortByRating, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Rating'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)

        # Sort by highest to lowest rating
        bookmarks.sort(key=self.sort_by_rating, reverse=True)

        context[self.context_object_name] = bookmarks
        return context


class SortByPopularity(BookmarksMixin, ListView):
    def sort_by_popularity(self, elem):
        return elem['review_count']

    def get_context_data(self, **kwargs):
        context = super(SortByPopularity, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Rating'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)

        # Sort by highest number of reviews to lowest number of reviews
        bookmarks.sort(key=self.sort_by_popularity, reverse=True)

        context[self.context_object_name] = bookmarks
        return context


class SortByDistance(BookmarksMixin, ListView):
    def sort_by_distance(self, elem):
        return elem['distance']

    def get_context_data(self, **kwargs):
        context = super(SortByDistance, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Rating'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)

                # Do business search to find distance from current location
                params = {'term': r['name'],
                          'location': location.CURRENT_LOCATION,
                          'categories': 'restaurants'}
                search_results = yelp_api.get("v3/businesses/search", params)['businesses']

                # Find matching business in search results
                for result in search_results:
                    if result['location']['address1'] == r['location']['address1']:
                        bookmarks.append(result)
                        break

        # Sort by closest to furthest away
        bookmarks.sort(key=self.sort_by_distance)

        context[self.context_object_name] = bookmarks
        return context
