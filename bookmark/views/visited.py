from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import VisitedForm
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


class AddToVisitedView(FormView):
    form_class = VisitedForm

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        business_id = form.cleaned_data.get('business_id')

        # Attempt retrieval of object from database
        try:
            r = Restaurant.objects.filter(business_id=business_id).get()
            if r.visited:
                # Object is already in visited, display warning message and redirect user to home page
                messages.warning(self.request, f'{name} is already in your visited list!')
                return redirect('bookmark-home')
            else:
                # Object is in bookmarks, move to visited and remove from bookmarks
                r.visited = True
                r.bookmark = False
                r.save()
        except exceptions.ObjectDoesNotExist:
            # Object does not yet exist, save to database
            form.save()

        # Display success message and redirect user to previous page
        messages.success(self.request, f'Added {name} to visited!')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        # Display error message and redirect user to previous page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect(self.request.META.get('HTTP_REFERER'))
