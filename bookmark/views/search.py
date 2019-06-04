from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import SearchForm
from bookmark.models import Restaurant


class Search(FormView, ListView):
    form_class = SearchForm

    model = Restaurant
    template_name = 'bookmark/home.html'
    context_object_name = 'restaurants'

    def form_valid(self, form):
        # Set search_term field in form
        SearchForm.search_term = form.cleaned_data['search_term']
        return redirect('search')

    def form_invalid(self, form):
        # Display error message and refresh page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)
        context['title'] = 'Searching...'

        # Additional parameters
        params = {'term': SearchForm.search_term,
                  'location': location.CURRENT_LOCATION,
                  'sort_by': 'best_match',
                  'categories': 'restaurants'}

        # Make Yelp Fusion API GET request for nearby restaurants
        restaurants = yelp_api.get("v3/businesses/search", params)

        context['restaurants'] = restaurants['businesses']
        return context


