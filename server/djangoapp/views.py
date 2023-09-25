from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
import asyncio
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)



def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index.html')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp/index.html")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = dict()
    
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7b4c0a85-5334-4549-aea8-89db1bd7b507/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships =  get_dealers_from_cf(url)
        context = {'dealership_list': dealerships}
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context= context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = dict()
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7b4c0a85-5334-4549-aea8-89db1bd7b507/dealership-package/get-review"
        results = get_dealer_reviews_from_cf(url, dealer_id = dealer_id)

        reviews = ' '.join([post.review + " " + post.sentiment for post in results])
        context = {'dealer_reviews': results, 'dealer_id': dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    car = [{"id": 1, "name": "Camry", "make": {"name": "Toyota"}, "year": 2021},
                {"id": 2, "name": "Highlander", "make": {"name": "Toyota"}, "year": 2011},
                {"id": 3, "name": "Rav4", "make": {"name": "Toyota"}, "year": 2022}]
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/7b4c0a85-5334-4549-aea8-89db1bd7b507/dealership-package/review"

     # Get username and password from request.POST dictionary
    # username = request.POST['username']
    # password = request.POST['psw']
    # # Try to check if provide credential can be authenticated
    # user = authenticate(username=username, password=password)
    # if user is not None:
    if request.method == "GET":
        context = dict()
        context = {"cars": car, "dealer_id": dealer_id}
        return render(request, 'djangoapp/add_review.html', context= context)
    elif request.method == "POST":
        review = dict()
        json_payload = dict()
        print(request.POST)
        curr_car = car[int(request.POST['car'])-1]
        review["id"] = 15
        review["name"] = "Trial running"
        review["dealership"] = dealer_id
        review["car_make"] = curr_car["make"]["name"]
        review["car_model"] = curr_car["name"]
        review["car_year"] = curr_car["year"]
        review["purchase"] = request.POST['purchasecheck']
        review["purchase_date"] = request.POST['purchasedate']
        review["review"] = request.POST['content']
        json_payload["review"] = review
        response = post_request(url, json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)


    
