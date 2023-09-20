import requests
import json
import asyncio
import time
from .models import CarDealer, DealerReview
# import related models here
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response =  requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
     
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    
    except Exception as err:
        print(f"An error occurred: {err}")

    status_code =  response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
  
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result =  get_request(url)
    if json_result:
        # Get the row list in JSON as dealers

        # For each dealer object
        for dealer in json_result["result"]["docs"]:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   state=dealer_doc["state"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result =  get_request(url, dealer_id = kwargs["dealer_id"])
    if json_result:
        # Get the row list in JSON as dealers

        # For each review object
        for review in json_result["docs"]:
            # Get its content in `doc` object
            review_doc = review
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(id=review_doc["id"], dealership=review_doc["dealership"], 
                                      name=review_doc["name"], purchase=review_doc["purchase"],
                                      review=review_doc["review"], purchase_date=review_doc["purchase_date"],
                                      car_make=review_doc["car_make"], car_model=review_doc["car_model"],
                                      car_year=review_doc["car_year"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)

            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealer_review):
    api_key = "R2s8l7dCGcgjSp4Z_Gl7CmUEOc0QBu3HXKQZzGYIvcJY"
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/edf934c8-ce9b-4edf-8489-f0a3e3b35c38"
    authenticator = IAMAuthenticator(api_key)
    NLU = NaturalLanguageUnderstandingV1(
                                        version='2022-04-07',
                                        authenticator=authenticator)
    NLU.set_service_url(url)
    response = NLU.analyze(text=dealer_review, features=Features(sentiment= SentimentOptions()), language= "en")
    sentiment = response.result["sentiment"]["document"]["label"]
    return sentiment





