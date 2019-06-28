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

        # Retrieve page number from URL
        page_num = 1
        if self.request.GET.get('page'):
            page_num = int(self.request.GET.get('page'))

        # Additional parameters
        params = {'location': location.CURRENT_LOCATION,
                  'sort_by': 'distance',
                  'categories': 'restaurants',
                  'offset': page_num * 20}

        # Make Yelp Fusion API GET request for nearby restaurants
        restaurants = yelp_api.get("v3/businesses/search", params)

        context[self.context_object_name] = restaurants['businesses']
        context['page'] = page_num
        return context
