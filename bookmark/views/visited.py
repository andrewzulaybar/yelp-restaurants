from django.views.generic import ListView

from bookmark.models import *


class VisitedListView(ListView):
    model = Restaurant
    template_name = 'bookmark/visited.html'
    context_object_name = 'restaurants'

    def get_context_data(self, **kwargs):
        context = super(VisitedListView, self).get_context_data(**kwargs)
        return self.get_visited(context)

    def get_visited(self, context):
        context['title'] = 'Visited'

        # Retrieve visited objects
        restaurants = Visited.objects.raw(
            ''' SELECT * 
                FROM bookmark_Visited v
                INNER JOIN bookmark_Restaurant r on v.restaurant_id = r.business_id
                INNER JOIN bookmark_Location l on r.location_id = l.id '''
        )

        # Format restaurants for template
        visited = []
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
            visited.append(res)

        context[self.context_object_name] = visited
        return context

