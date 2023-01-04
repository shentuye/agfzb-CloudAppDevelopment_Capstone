import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1  import Features, CategoriesOptions, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "api_key" in kwargs:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', kwargs["api_key"]))
        else:
            # no authentication GET
                    # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
        return False
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("Post to {} {}".format(url, json_payload))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
        return False
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"],
                                   state=dealer_doc["state"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,  dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"],
                                   state=dealer_doc["state"])
            results.append(dealer_obj)

    return results

def get_dealers_by_state(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,  state=state )
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj =CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"],
                                   state=dealer_doc["state"])
            results.append(dealer_obj)

    return results    

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,  dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["data"]["docs"]
        # For each dealer object
        for review in reviews:
            # Create a CarDealer object with values in `doc` object
            review_obj =  DealerReview(review["dealership"], review["name"], review["purchase"], 
            review["review"], review["purchase_date"], review["car_make"], review["car_model"], 
            review["car_year"], review["id"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results     

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/fc1b576e-0b7c-499a-9e82-63cc479a7029"

    api_key = "Obyt1mB7hiix8tqUumi6SO-TrT6fNDEkc76rXCq3HEvu" 
    try:
        authenticator = IAMAuthenticator(api_key) 

        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 

        natural_language_understanding.set_service_url(url) 

        response = natural_language_understanding.analyze( text=dealerreview+"hello hello hello" ,
        features=Features(sentiment=SentimentOptions(targets=[dealerreview+"hello hello hello"]))).get_result()

        label=json.dumps(response, indent=2) 

        label = response['sentiment']['document']['label'] 
        return label
    except:
        label = 'positive'

        return label
    




