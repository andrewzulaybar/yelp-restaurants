import requests

import secrets

# API constants
API_URL = "https://www.googleapis.com/"
API_PATH = "geolocation/v1/geolocate?key="

# Set up parameter for API request
url = API_URL + API_PATH + secrets.GOOGLE_API_KEY

response = requests.post(url)

if response.status_code == 200:
    # Obtain (latitude, longitude) pair from JSON response
    lat = response.json()['location']['lat']
    long = response.json()['location']['lng']
    CURRENT_LOCATION = str(lat) + ", " + str(long)
else:
    print("HTTP request error: %s" % response.status_code)

