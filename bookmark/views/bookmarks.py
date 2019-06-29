from django.views.generic import ListView

from bookmark.api import location, yelp_api
from bookmark.forms import *
from bookmark.models import *


class BookmarksMixin(object):
    model = Bookmarks
    template_name = 'bookmark/bookmarks.html'
    context_object_name = 'restaurants'
    paginate_by = 10

    # Additional parameters
    params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

    def add_to_context(self, bookmarks, restaurants):
        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)


class BookmarksListView(BookmarksMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(BookmarksListView, self).get_context_data(**kwargs)
        form = SortByForm(self.request.GET or None)

        if form.is_valid():
            # Sort businesses by given parameter
            sort_by = form.cleaned_data['sort_by']
            if sort_by == 'Distance':
                context = self.sort_by_distance(context)
            elif sort_by == 'Popularity':
                context = self.sort_by_popularity(context)
            elif sort_by == 'Rating':
                context = self.sort_by_rating(context)
            elif sort_by == 'Cuisine':
                context = self.sort_by_cuisine(context)
            elif sort_by == 'Price':
                context = self.sort_by_price(context)
            elif sort_by == 'Open Now':
                context = self.is_open_now(context)
            else:
                # Sort by 'Date Added'
                context = self.get_bookmarks(context)
        else:
            # Form is invalid or form is None: sort by default
            context = self.get_bookmarks(context)
            self.ordering = ['date']
        return context

    @staticmethod
    def get_bookmarks(context):
        context['title'] = 'Bookmarks'

        # Retrieve restaurants for each bookmark
        restaurants = []
        for bookmark in context['restaurants']:
            restaurants.append(bookmark.restaurant_id)
        context['restaurants'] = Restaurant.objects.filter(business_id__in=restaurants)

        # Retrieve categories for each restaurant
        categories = []
        for restaurant in context['restaurants']:
            category = RestaurantHasCategory.objects.filter(restaurant=restaurant)
            categories.append(category[0])
        context['categories'] = categories

        return context

    def sort_by_distance(self, context):
        context['title'] = 'Bookmarks - Sort by Distance'

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
        bookmarks.sort(key=self.__distance)

        context[self.context_object_name] = bookmarks
        return context

    def sort_by_popularity(self, context):
        context['title'] = 'Bookmarks - Sort by Popularity'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort by highest number of reviews to lowest number of reviews
        bookmarks.sort(key=self.__popularity, reverse=True)

        context[self.context_object_name] = bookmarks
        return context

    def sort_by_rating(self, context):
        context['title'] = 'Bookmarks - Sort by Rating'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort by highest to lowest rating
        bookmarks.sort(key=self.__rating, reverse=True)

        context[self.context_object_name] = bookmarks
        return context

    def sort_by_cuisine(self, context):
        context['title'] = 'Bookmarks - Sort by Cuisine'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort alphabetically by first category title
        bookmarks.sort(key=self.__cuisine)

        context[self.context_object_name] = bookmarks
        return context

    def sort_by_price(self, context):
        context['title'] = 'Bookmarks - Sort by Price'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort by cheapest to most expensive
        bookmarks.sort(key=self.__price)

        context[self.context_object_name] = bookmarks
        return context

    def is_open_now(self, context):
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

    @staticmethod
    def __distance(elem):
        return elem['distance']

    @staticmethod
    def __popularity(elem):
        return elem['review_count']

    @staticmethod
    def __rating(elem):
        return elem['rating']

    @staticmethod
    def __cuisine(elem):
        return elem['categories'][0]['title']

    @staticmethod
    def __price(elem):
        try:
            return elem['price']
        except KeyError:
            return ""
