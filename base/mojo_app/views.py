from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, TripCreationForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from openai import OpenAI
from pydantic import BaseModel
import json
from django.shortcuts import get_object_or_404
from typing import List

# Create your views here.

@login_required(login_url='mojo:login')
def index(request):
    """
    Renders the index page, which contains a list of trips
    created by the currently logged in user.
    """
    trips = Trip.objects.filter(created_by=request.user)
    for t in trips:
      print(1)
      print(t.uuid)
    return render(request, 'index.html', {'user': request.user, 'trips': trips})


def login_view(request):
  """
  Renders the login page, which contains a form for users to
  submit their email and password.
  """
  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = CustomUser.objects.filter(email=email).first()
    if user and user.check_password(password):
      login(request, user)
      return redirect('mojo:index')

  return render(request, 'login.html')


def signup(request):
  """
  Renders the signup page, which contains a form for
  users to submit their name, email, password, confirm password,
  zip code, and date of birth.
  """
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    print('before form is valid')
    for f in form:
      print(f.name, f.value(), f.errors)
    print('after f in form')
    if form.is_valid():
      print("form is valid")
      user = form.save()
      login(request, user)
      return redirect('mojo:index')
    else:
      print("form is not valid")
  form = CustomUserCreationForm()
  return render(request, 'signup.html', {'form': form})


def profile(request):

  """
  Renders the user's profile page.
  """
  return render(request, 'profile.html')



def create_trip(request):
    """
    Handles GET and POST requests for creating a new trip.

    On a GET, renders the create_trip.html template with a blank
    TripCreationForm.

    On a valid POST, creates a new Trip object in the database with
    the submitted form data, associates it with the currently logged
    in user, and redirects to the index page.
    """
    if request.method == 'POST':
        form = TripCreationForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.created_by = request.user
            trip.save()
            print("Trip created:", trip)
            return redirect('mojo:index')
    else:
        form = TripCreationForm()
    return render(request, 'create_trip.html', {'form': form})


@login_required(login_url='mojo:login')
def trip(request, trip_id):
    trip = get_object_or_404(Trip, uuid=trip_id)
    activities = trip.userenteredactivity_set.all()
    model_suggestions = ModelTripActivity.objects.filter(trip=trip)
    return render(request, 'trip.html', {'trip': trip,
                                         'activities': activities,
                                         'model_suggestions': model_suggestions})


@login_required(login_url='mojo:login')
def add_activity(request, trip_id):
    """
    Handles POST requests from the trip details page
    to add a new activity to the specified trip.
    Redirects back to the trip details page after adding the activity.
    """

    trip = Trip.objects.get(uuid=trip_id)
    if request.method == 'POST':
        activity_name = request.POST.get('activity_name')
        activity = UserEnteredActivity(activity_name=activity_name,
                                       trip=trip,
                                       created_by=request.user)
        activity.save()
    return redirect('mojo:trip', trip_id)

@login_required(login_url='mojo:login')
def generate_itinerary(request, trip_id):
  """
  Generates an itinerary for a specified trip using OpenAI's API.

  This function retrieves the trip and its associated activities based on the
  provided trip ID. It then generates an itinerary using OpenAI's API by
  passing the trip's destination and dates, along with the names of the
  first three activities. Finally, it returns the generated itinerary in a
  JSON response.

  Args:
      request: The HTTP request object.
      trip_id: The ID of the trip for which the itinerary is being generated.

  Returns:
      JsonResponse: A JSON response containing the generated itinerary.
  """
  trip = Trip.objects.get(uuid = trip_id)
  activities = UserEnteredActivity.objects.filter(trip=trip)
  client = OpenAI()
  serialized_start_date = trip.start_date.strftime("%Y-%m-%d")
  serialized_end_date = trip.end_date.strftime("%Y-%m-%d")
  serialized_activities = serialize('json', activities)


  response = client.responses.create(
    prompt={
        "id": "pmpt_689e839191808196aee8f2537e3c63770d2c7182b27d433c",
        "version": "3",
        "variables": {
          "travel_destination": trip.destination,
          "trip_start_date": serialized_start_date,
          "trip_end_date": serialized_end_date,
          "activities": serialized_activities
      }
    }
)

  activities_list = json.loads(response.output[0].content[0].text)

# If there are already suggestions for this trip, delete them
  ModelTripActivity.objects.filter(trip=trip).delete()
  for activity in activities_list:
    ModelTripActivity.objects.create(
      trip=trip,
      name=activity['activity_name'],
      description=activity['activity_description'],
      location_string=activity['place'],
      url=activity['place_url']
    )

  return redirect('mojo:trip', trip_id)

