import requests

import secrets

# API constants
API_URL = "https://www.googleapis.com/"
API_PATH = "geolocation/v1/geolocate?key="

# Set up parameter for API request
url = API_URL + API_PATH + secrets.GOOGLE_API_KEY

try:
    # Send POST request to Google Maps Geolocation API
    response = requests.post(url)

    # If successful, obtain (latitude, longitude) pair from JSON response
    lat = response.json()['location']['lat']
    long = response.json()['location']['lng']
    CURRENT_LOCATION = str(lat) + ", " + str(long)
except requests.exceptions.RequestException as error:
    # Otherwise, print error
    print(error)
