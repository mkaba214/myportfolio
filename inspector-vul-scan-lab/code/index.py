import requests
from requests.exceptions import RequestException

def lambda_handler(event, context):

    try:
        # Make a GET request to a URL
        response = requests.get("https://api.example.com/data")

        # Check if the request was successful
        if response.status_code == 200:
            # Get the JSON data from the response
            data = response.json()
            return data
        else:
            # Handle the error
            return {
                "statusCode": response.status_code,
                "body": response.text
            }

    except RequestException as e:
        # Handle the case where the server is down or unreachable
        return {
            "statusCode": 503,
            "body": "Service Unavailable"
        }