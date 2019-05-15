from django.views.generic import ListView

from bookmark.api import location, yelp_api
from bookmark.models import Restaurant


class HomeListView(ListView):
    model = Restaurant
    template_name = 'bookmark/home.html'
    context_object_name = 'restaurants'

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        context['title'] = 'Home Page'

        # Additional parameters
        params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

        # Make Yelp Fusion API GET request for nearby restaurants
        restaurants = yelp_api.get("v3/businesses/search", params)

        context['restaurants'] = restaurants['businesses']
        return context
