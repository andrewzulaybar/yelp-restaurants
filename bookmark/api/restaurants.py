from bookmark.api import location, yelp_api

# API constants
API_PATH = "v3/businesses/search"

# Additional parameters
params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

# Make Yelp Fusion API GET request for nearby restaurants
restaurants = yelp_api.get(API_PATH, params)
RESTAURANTS = restaurants['businesses']
