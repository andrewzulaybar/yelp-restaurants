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

try:
    # Send GET request to Yelp Fusion API
    response = requests.get(url=url, headers=headers, params=params)

    # If successful, obtain restaurant data from JSON response
    RESTAURANTS = response.json()['businesses']
except requests.exceptions.RequestException as error:
    # Otherwise, print error
    print(error)
