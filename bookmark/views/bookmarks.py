from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import BookmarkForm, SortByForm
from bookmark.models import Restaurant


class BookmarksMixin(object):
    model = Restaurant
    template_name = 'bookmark/bookmarks.html'
    context_object_name = 'restaurants'

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
        return context

    def get_bookmarks(self, context):
        context['title'] = 'Bookmarks'

        bookmarks = []
        restaurants = Restaurant.objects.all()

        # If restaurants in database are bookmarked, pull data from Yelp Fusion API
        for restaurant in restaurants:
            if restaurant.bookmark:
                r = yelp_api.get("v3/businesses/" + restaurant.business_id, self.params)
                bookmarks.append(r)

        context[self.context_object_name] = bookmarks
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

    def __distance(self, elem):
        return elem['distance']

    def __popularity(self, elem):
        return elem['review_count']

    def __rating(self, elem):
        return elem['rating']

    def __cuisine(self, elem):
        return elem['categories'][0]['title']

    def __price(self, elem):
        try:
            return elem['price']
        except KeyError:
            return ""


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
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        # Display error message and redirect user to home page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect(self.request.META.get('HTTP_REFERER'))
