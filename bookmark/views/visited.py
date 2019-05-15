from django.views.generic import ListView

from bookmark.api import location, yelp_api
from bookmark.models import Restaurant


class VisitedListView(ListView):
    model = Restaurant
    template_name = 'bookmark/visited.html'
    context_object_name = 'restaurants'

    def get_context_data(self, **kwargs):
        context = super(VisitedListView, self).get_context_data(**kwargs)
        context['title'] = 'Visited'

        # Additional parameters
        params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

        # If restaurants in database have been visited, pull data from Yelp Fusion API
        visited = []
        restaurants = Restaurant.objects.all()
        for restaurant in restaurants:
            if restaurant.visited:
                restaurant = yelp_api.get("v3/businesses/" + restaurant.business_id, params)
                visited.append(restaurant)

        context['restaurants'] = visited
        return context
