from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import BookmarkForm
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


class AddToBookmarksView(FormView):
    form_class = BookmarkForm

    def form_valid(self, form):
        # Save name and business_id
        name = form.cleaned_data.get('name')
        business_id = form.cleaned_data.get('business_id')

        # Attempt retrieval of object from database
        try:
            r = Restaurant.objects.filter(business_id=business_id).get()
            if r.bookmark:
                # Object is already in bookmarks, display warning message
                messages.warning(self.request, f'{name} is already in your bookmarks list!')
            else:
                # Object is in visited, display warning message
                messages.warning(self.request, f'{name} is in your visited list!')
        except exceptions.ObjectDoesNotExist:
            # Object does not yet exist, save to database and display success message
            form.save()
            messages.success(self.request, f'Added {name} to bookmarks!')

        # Redirect user to home page
        return redirect('bookmark-home')

    def form_invalid(self, form):
        # Display error message and redirect user to home page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect('bookmark-home')
