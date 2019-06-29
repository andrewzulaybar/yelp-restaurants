import requests

import secrets

# API constants
API_URL = 'https://maps.googleapis.com/maps/api/distancematrix/'
OUTPUT_FORMAT = 'json'


def get_distance(origins, destinations):
    """
    If Google Distance Matrix API request is successful, returns JSON object from response. Otherwise, prints error.

    Args:
        origins (string): String containing list of starting points, separated by pipe character.
        destinations (string): String containing list of destination points, separated by pipe character.

    Returns:
        JSON object from Google Distance Matrix API GET request.
    """
    # Set up parameters for API request
    params = {
        'origins': origins,
        'destinations': destinations,
        'key': secrets.GOOGLE_API_KEY
    }

    url = API_URL + OUTPUT_FORMAT + '?'

    # Send GET request to Google Distance Matrix API
    response = requests.get(url=url, params=params).json()

    # Construct list of distances
    distances = []
    for row in response['rows']:
        for item in row['elements']:
            distances.append(item['distance']['text'])

    return distances
