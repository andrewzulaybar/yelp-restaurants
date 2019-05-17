from django.views.generic import ListView

from bookmark.api import location, yelp_api
from bookmark.models import Restaurant


class BookmarksListView(ListView):
    model = Restaurant
    template_name = 'bookmark/bookmarks.html'
    context_object_name = 'restaurants'

    def get_context_data(self, **kwargs):
        context = super(BookmarksListView, self).get_context_data(**kwargs)
        context['title'] = 'Bookmarks'

        # Additional parameters
        params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        bookmarks = []
        restaurants = Restaurant.objects.all()

        for restaurant in restaurants:
            if restaurant.bookmark:
                restaurant = yelp_api.get("v3/businesses/" + restaurant.business_id, params)
                bookmarks.append(restaurant)

        context['restaurants'] = bookmarks
        return context
