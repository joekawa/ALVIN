from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, TripCreationForm
from .models import CustomUser, Trip, Activity
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='mojo:login')
def index(request):
    """
    Renders the index page, which contains a list of trips
    created by the currently logged in user.
    """
    trips = Trip.objects.filter(created_by=request.user)
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
  Renders the page for creating a new trip.
  """
  return render(request, 'create_trip.html')



def create_trip(request):
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
    trip = Trip.objects.get(id=trip_id)
    return render(request, 'trip.html', {'trip': trip})


@login_required(login_url='mojo:login')
def add_activity(request, trip_id):
    """
    Handles POST requests from the trip details page
    to add a new activity to the specified trip.
    Redirects back to the trip details page after adding the activity.
    """

    trip = Trip.objects.get(id=trip_id)
    if request.method == 'POST':
        activity_name = request.POST.get('activity_name')
        activity = Activity(name=activity_name, trip=trip)
        activity.save()
    return redirect('mojo:trip', trip_id)