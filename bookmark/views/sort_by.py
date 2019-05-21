from django.views.generic import ListView

from bookmark.api import location, yelp_api
from bookmark.models import Restaurant
from bookmark.views import BookmarksMixin


class SortByDistance(BookmarksMixin, ListView):
    def sort_by_distance(self, elem):
        return elem['distance']

    def get_context_data(self, **kwargs):
        context = super(SortByDistance, self).get_context_data(**kwargs)
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
        bookmarks.sort(key=self.sort_by_distance)

        context[self.context_object_name] = bookmarks
        return context


class SortByPopularity(BookmarksMixin, ListView):
    def sort_by_popularity(self, elem):
        return elem['review_count']

    def get_context_data(self, **kwargs):
        context = super(SortByPopularity, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Popularity'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort by highest number of reviews to lowest number of reviews
        bookmarks.sort(key=self.sort_by_popularity, reverse=True)

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
        self.add_to_context(bookmarks, restaurants)

        # Sort by highest to lowest rating
        bookmarks.sort(key=self.sort_by_rating, reverse=True)

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
        self.add_to_context(bookmarks, restaurants)

        # Sort alphabetically by first category title
        bookmarks.sort(key=self.sort_by_cuisine)

        context[self.context_object_name] = bookmarks
        return context


class SortByPrice(BookmarksMixin, ListView):
    def sort_by_price(self, elem):
        try:
            return elem['price']
        except KeyError:
            return ""

    def get_context_data(self, **kwargs):
        context = super(SortByPrice, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks - Sort by Price'

        bookmarks = []
        restaurants = Restaurant.objects.all()
        self.add_to_context(bookmarks, restaurants)

        # Sort by cheapest to most expensive
        bookmarks.sort(key=self.sort_by_price)

        context[self.context_object_name] = bookmarks
        return context


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
