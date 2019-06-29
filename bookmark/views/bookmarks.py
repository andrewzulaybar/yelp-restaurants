from django.views.generic import ListView
from django.core.paginator import Paginator

from bookmark.api import location, distance_matrix
from bookmark.forms import *
from bookmark.models import *


class BookmarksListView(ListView):
    model = Bookmarks
    template_name = 'bookmark/bookmarks.html'
    context_object_name = 'restaurants'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        # Retrieve restaurants for each bookmark
        restaurants = self.get_restaurants(Bookmarks.objects.all())

        form = SortByForm(self.request.GET or None)
        if form.is_valid():
            # Turn off pagination
            self.paginate_by = 0

            # Sort businesses by given parameter
            sort_by = form.cleaned_data['sort_by']
            if sort_by == 'Distance':
                # Sort by distance ascending
                queryset = self.sort_by_distance(restaurants)
            elif sort_by == 'Popularity':
                # Sort by review count descending
                queryset = Restaurant.objects.filter(business_id__in=restaurants).order_by('-review_count')
            elif sort_by == 'Rating':
                # Sort by rating descending
                queryset = Restaurant.objects.filter(business_id__in=restaurants).order_by('-rating')
            elif sort_by == 'Price':
                # Sort by price ascending
                queryset = Restaurant.objects.filter(business_id__in=restaurants).order_by('price')
            else:
                # Sort by date added
                queryset = Restaurant.objects.filter(business_id__in=restaurants)
        else:
            queryset = Restaurant.objects.filter(business_id__in=restaurants)
        return queryset

    def get_context_data(self, **kwargs):
        form = SortByForm(self.request.GET or None)
        context = super(BookmarksListView, self).get_context_data(**kwargs)

        if form.is_valid():
            sort_by = form.cleaned_data['sort_by']
            if sort_by == 'Distance':
                context['title'] = 'Bookmarks - Sorted by Distance'
            elif sort_by == 'Popularity':
                context['title'] = 'Bookmarks - Sorted by Popularity'
            elif sort_by == 'Rating':
                context['title'] = 'Bookmarks - Sorted by Rating'
            elif sort_by == 'Price':
                context['title'] = 'Bookmarks - Sorted by Price'
            else:
                context['title'] = 'Bookmarks'
        else:
            context['title'] = 'Bookmarks'

        # Retrieve categories for each restaurant
        context['categories'] = self.get_categories(context[self.context_object_name])

        return context

    @staticmethod
    def sort_by_distance(restaurants):
        # Retrieve restaurants for each bookmark
        queryset = Restaurant.objects.filter(business_id__in=restaurants)

        # Calculate distances from current location to each restaurant
        destinations = ""
        for restaurant in list(queryset)[:-1]:
            destinations += str(restaurant.location.latitude) + ',' + str(restaurant.location.longitude) + '|'
        else:
            destinations += str(list(queryset)[-1].location.latitude) \
                            + ',' + str(list(queryset)[-1].location.longitude)
        distances = distance_matrix.get_distance(location.CURRENT_LOCATION.replace(" ", ""), destinations)

        # Construct (restaurant, distance) pairs to allow for sorting
        object_list = {}
        for restaurant, distance in zip(queryset, distances):
            object_list[restaurant] = distance

        # Once sorted by distance in increasing order, retrieve only restaurant objects
        queryset = [pair[0] for pair in sorted(object_list.items(), key=lambda x: x[1])]

        return queryset

    @staticmethod
    def get_restaurants(restaurants):
        object_list = []
        for bookmark in restaurants:
            object_list.append(bookmark.restaurant_id)
        return object_list

    @staticmethod
    def get_categories(restaurants):
        categories = []
        for restaurant in restaurants:
            category = RestaurantHasCategory.objects.filter(restaurant=restaurant)
            categories.append(category[0])
        return categories
