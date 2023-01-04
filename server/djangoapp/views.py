from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealers_by_state, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import generic
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
class CarListView(generic.ListView):
    model = CarModel
    template_name = 'djangoapp/add_review.html'
    context_object_name = 'cars'


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html', None)


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html', None)

# Create a `login_request` view to handle sign in request
def login_request(request):
    global user
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/registration.html', context)
    else:
        return render(request, 'djangoapp/registration.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):  
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    global user
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/570290ab-05ca-4421-bb98-a931d8aba952/dealership-package/dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        print(dealer_names)        
        keys = ["ID", "Dealer Name", "City", "Address", "Zip", "State"]
        return render(request, 'djangoapp/index.html', 
        {"keys":keys, "dealership_list":dealerships})
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/570290ab-05ca-4421-bb98-a931d8aba952/dealership-package/review"
    reviews = get_dealer_reviews_from_cf(url, dealer_id)
    # Concat all dealer's short name
    reviewsstr = ' '.join([f"{re.name} {re.review} {re.sentiment};" for re in reviews])
    # Return a list of dealer short name
    print(reviewsstr)
    context = { "reviews": reviews, "dealer_id": dealer_id}
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    response = None
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/570290ab-05ca-4421-bb98-a931d8aba952/dealership-package/post_review"
    cars = list(CarModel.objects.all())
    if request.user.is_authenticated and request.method=="POST":
        car = CarModel.objects.get(id=request.POST['car'])
        review = {
        "id":123,
        "name": request.user.username,
        "dealership": dealer_id,
        "review": request.POST['content'],
        "purchase": request.POST['purchasecheck'],
        "purchase_date": datetime.utcnow().isoformat(),
        "car_make": car.carMake.name,
        "car_model": car.name,
        "car_year": car.year.strftime("%Y")
        }
        json_payload = {"review": review}
        response = post_request(url, json_payload=json_payload)
        print(json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    elif request.user.is_authenticated and request.method=="GET":       
        context = {  "dealer_id": dealer_id, "cars": cars}
        return render(request, 'djangoapp/add_review.html', context)


    

