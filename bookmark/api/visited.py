from bookmark.api import location, yelp_api
from bookmark.models import Restaurant

# API constants
API_PATH = "v3/businesses/"

# Additional parameters
params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

# If restaurants in database have been visited, pull data from Yelp Fusion API
RESTAURANTS = []
restaurants = Restaurant.objects.all()

for restaurant in restaurants:
    if restaurant.visited:
        restaurant = yelp_api.get(API_PATH + restaurant.business_id, params)
        RESTAURANTS.append(restaurant)
