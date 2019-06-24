import ast
import datetime
from django.contrib import messages
from django.core import exceptions
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from bookmark.api import location, yelp_api
from bookmark.forms import *
from bookmark.models import *


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

        # Retrieve bookmark objects
        restaurants = Bookmarks.objects.raw(
            ''' SELECT * 
                FROM bookmark_Bookmarks b
                INNER JOIN bookmark_Restaurant r on b.restaurant_id = r.business_id
                INNER JOIN bookmark_Location l on r.location_id = l.id 
                ORDER BY date DESC '''
        )

        # Format restaurants for template
        bookmarks = []
        for restaurant in restaurants:
            # Retrieve categories for restaurant
            categories = []
            all_categories = Category.objects.raw(
                ''' SELECT *
                    FROM bookmark_Restaurant r
                    INNER JOIN bookmark_RestaurantHasCategory rhc ON r.business_id = rhc.restaurant_id
                    INNER JOIN bookmark_Category c ON rhc.category_id = c.title
                    WHERE r.business_id = '%s' ''' % restaurant.business_id
            )
            for category in all_categories:
                categories.append(category.title)

            # Setup context for template
            res = {
                'business_id': restaurant.business_id,
                'name': restaurant.name,
                'rating': restaurant.rating,
                'review_count': restaurant.review_count,
                'price': restaurant.price,
                'phone': restaurant.phone,
                'image_url': restaurant.image_url,
                'yelp_url': restaurant.yelp_url,
                'location_id': restaurant.location_id,
                'address': restaurant.address,
                'categories': categories
            }
            bookmarks.append(res)

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

    @staticmethod
    def __distance(elem):
        return elem['distance']

    @staticmethod
    def __popularity(elem):
        return elem['review_count']

    @staticmethod
    def __rating(elem):
        return elem['rating']

    @staticmethod
    def __cuisine(elem):
        return elem['categories'][0]['title']

    @staticmethod
    def __price(elem):
        try:
            return elem['price']
        except KeyError:
            return ""


class AddToBookmarksView(FormView):
    def post(self, request, *args, **kwargs):
        # Process bookmark, category, and location forms
        bookmark_form = BookmarkForm(request.POST, prefix='bookmark')
        category_form = CategoryForm(request.POST, prefix='category')
        location_form = LocationForm(request.POST, prefix='location')

        if bookmark_form.is_valid() and location_form.is_valid():
            self.bookmark_and_location_form_valid(bookmark_form, location_form)

        if bookmark_form.is_valid() and category_form.is_valid() and location_form.is_valid():
            self.bookmark_and_location_form_valid(bookmark_form, location_form)
            self.category_form_valid(category_form, bookmark_form)
        else:
            name = bookmark_form['name'].value()
            business_id = bookmark_form['business_id'].value()

            # Attempt retrieval of object from Restaurant relation
            try:
                restaurant = Restaurant.objects.filter(pk=business_id).get()
                if Bookmarks.objects.filter(restaurant=restaurant).exists():
                    # Object is already in bookmarks, display warning message
                    messages.warning(self.request, f'{name} is already in your bookmarks!')
                elif Visited.objects.filter(restaurant=restaurant).exists():
                    # Object is already in visited, display warning message
                    messages.warning(self.request, f'{name} is in your visited list!')
                else:
                    # Display error message, look into problem
                    messages.error(self.request, 'An error occured! Please try again later.', extra_tags='danger')
            except exceptions.ObjectDoesNotExist:
                # Display error message, look into problem
                messages.error(self.request, 'An error occured! Please try again later.', extra_tags='danger')

        return redirect(self.request.META.get('HTTP_REFERER'))

    def bookmark_and_location_form_valid(self, bookmark_form, location_form):
        business_id = bookmark_form.cleaned_data.get('business_id')
        name = bookmark_form.cleaned_data.get('name')
        rating = bookmark_form.cleaned_data.get('rating')
        review_count = bookmark_form.cleaned_data.get('rating')
        price = bookmark_form.cleaned_data.get('price')
        phone = bookmark_form.cleaned_data.get('phone')
        image_url = bookmark_form.cleaned_data.get('image_url')
        yelp_url = bookmark_form.cleaned_data.get('yelp_url')
        address = location_form.cleaned_data.get('address')
        postal_code = location_form.cleaned_data.get('postal_code')

        # Save location if not already in Location relation
        if not Location.objects.filter(address=address, postal_code=postal_code).exists():
            location_form.save()

        # Save restaurant and create bookmark if not already in Restaurant relation
        if not Restaurant.objects.filter(pk=business_id).exists():
            loc = Location.objects.get(address=address, postal_code=postal_code)
            restaurant = Restaurant.objects.create_restaurant(business_id, name, rating, review_count,
                                                              price, phone, image_url, yelp_url, loc)
            Bookmarks.objects.create_bookmark(date=datetime.datetime.now(), restaurant=restaurant).save()
            messages.success(self.request, f'Added {name} to bookmarks!')

    @staticmethod
    def category_form_valid(category_form, bookmark_form):
        categories = ast.literal_eval(category_form.cleaned_data.get('categories'))
        business_id = bookmark_form.cleaned_data.get('business_id')

        for category in categories:
            # Save category if not already in Category relation
            title = category['title']
            alias = category['alias']
            if not Category.objects.filter(title=title, alias=alias).exists():
                Category.objects.create_category(title=title, alias=alias).save()
            # Save (business_id, category) pair if not already in RestaurantHasCategory relation
            restaurant = Restaurant.objects.filter(pk=business_id)[0]
            category = Category.objects.filter(title=title, alias=alias)[0]
            if not RestaurantHasCategory.objects.filter(restaurant=restaurant, category=category).exists():
                RestaurantHasCategory.objects.create_object(restaurant, category).save()
