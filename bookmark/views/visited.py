from django.views.generic import ListView

from bookmark.models import *


class VisitedListView(ListView):
    model = Visited
    template_name = 'bookmark/visited.html'
    context_object_name = 'restaurants'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(VisitedListView, self).get_context_data(**kwargs)
        return self.get_visited(context)

    @staticmethod
    def get_visited(context):
        context['title'] = 'Visited'

        # Retrieve restaurants for each in visited
        restaurants = []
        for visited in context['restaurants']:
            restaurants.append(visited.restaurant_id)
        context['restaurants'] = Restaurant.objects.filter(business_id__in=restaurants)

        # Retrieve categories for each restaurant
        categories = []
        for restaurant in context['restaurants']:
            category = RestaurantHasCategory.objects.filter(restaurant=restaurant)
            categories.append(category[0])
        context['categories'] = categories
        return context

