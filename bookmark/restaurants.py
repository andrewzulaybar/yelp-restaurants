import requests

from bookmark import location
import secrets

# API constants
API_URL = "https://api.yelp.com/"
API_PATH = "v3/businesses/search"

# Set up parameters for API request
url = API_URL + API_PATH
headers = {'authorization': 'bearer %s' % secrets.YELP_API_KEY}
params = {'location': location.CURRENT_LOCATION, 'sort_by': 'distance', 'categories': 'restaurants'}

response = requests.get(url=url, headers=headers, params=params)

if response.status_code == 200:
    # Obtain restaurant data from JSON response
    RESTAURANTS = response.json()
else:
    print("HTTP request error: %s" % response.status_code)
