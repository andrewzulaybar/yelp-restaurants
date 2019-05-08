import requests

import secrets


def get(path, params):
    """
    If Yelp Fusion API GET request is successful, returns JSON object from response. Otherwise, prints error.

    Args:
        path (string): The API endpoint of interest.
        params (dict): Extra parameters.

    Returns:
        JSON object from Yelp Fusion API GET request.
    """
    # Set up parameters for API request
    url = "https://api.yelp.com/" + path
    headers = {'authorization': 'bearer %s' % secrets.YELP_API_KEY}

    try:
        # Send GET request to Yelp Fusion API
        response = requests.get(url=url, headers=headers, params=params)

        # If successful, obtain restaurant data from JSON response
        return response.json()
    except requests.exceptions.RequestException as error:
        # Otherwise, print error
        print(error)
