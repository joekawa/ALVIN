from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, TripCreationForm, ProfileForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from openai import OpenAI
from django.utils import timezone
from django.db.models import Max
import json
import re

# Create your views here.

#* I NEED TO UPDATE THIS TO CHECK FOR ALL TRIPS THE USER HAS CREATED
#* OR IS A PARTICIPANT OF
@login_required(login_url='mojo:login')
def index(request):
    """
    Renders the index page, which contains a list of trips
    created by the currently logged in user.
    """
    include_past = request.GET.get('show_past') in ['1', 'true', 'True']
    trips = Trip.objects.filter(tripparticipant__user=request.user)
    if not include_past:
        today = timezone.now().date()
        trips = trips.filter(end_date__gte=today)

    return render(request, 'index.html', {
        'user': request.user,
        'trips': trips,
        'include_past': include_past,
    })

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
      # Determine where to redirect back to: POST next, then GET next, then referer
      next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or request.META.get('HTTP_REFERER')
        or ''
      )
      if isinstance(next_url, str) and next_url.startswith('/'):
        return redirect(next_url)
      return redirect('mojo:index')
    # If credentials invalid, fall through to render login page again
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
      shared_trip = SharedTrip.objects.get(shared_with=user.email)
      trip_participant = TripParticipant.objects.create(trip=shared_trip.trip,
                                                       user=user,
                                                       role="contributor")
      login(request, user)
      return redirect('mojo:index')
    else:
      print("form is not valid")
  form = CustomUserCreationForm()
  return render(request, 'signup.html', {'form': form})

@login_required(login_url='mojo:welcome')
def profile(request):

  """
  Renders the user's profile page.
  """
  print('profile view')

  if request.method == 'POST':
      form = ProfileForm(request.POST, instance=request.user)
      if form.is_valid():
          form.save()
          return render(request, 'profile.html', {'form': form})
  else:
      form = ProfileForm(instance=request.user)
  return render(request, 'profile.html', {'form': form})


@login_required(login_url='mojo:welcome')
def create_trip_form(request):
  form = TripCreationForm()
  return render(request, 'create_trip.html', {'form': form})

@login_required(login_url='mojo:welcome')
def create_trip(request):
    """
    Handles GET and POST requests for creating a new trip.

    On a GET, renders the create_trip.html template with a blank
    TripCreationForm.

    On a valid POST, creates a new Trip object in the database with
    the submitted form data, associates it with the currently logged
    in user, and redirects to the index page.
    """
    form = TripCreationForm()
    #* NEED TO HAVE TRIPCONTRIBUTOR OBJECT CREATED WHEN A TRIP IS CREATED
    if request.method == 'POST':
        destination = request.POST.get('destination') #* AUTOCOMPLETE VALUE IN FORM
        trip_name = request.POST.get('trip_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        pattern = re.compile(r'(?P<city>.+?),\s+(?P<state>\w+),\s+(?P<country>.+)')
        match = pattern.match(destination)
        if match:
          city = match.group('city')
          state = match.group('state')
          country = match.group('country')
        else:
          city = None
          state = None
          country = None
        trip = Trip.objects.create(trip_name=trip_name, start_date=start_date,
                                   end_date=end_date,  destination_city=city,
                                   destination_state=state,
                                   created_by=request.user)
        trip.save()
        trip_participant = TripParticipant.objects.create(trip=trip,
                                                          user=request.user,
                                                          role="owner")
        trip_participant.save()
        #if form.is_valid():
         #   trip = form.save(commit=False)
          #  trip.created_by = request.user
           # trip.save()
            #TripParticipant.objects.create(trip=trip, user=request.user,
             #                              role="owner")
            #print("Trip created:", trip)
           # return redirect('mojo:index')
    #else:
       # form = TripCreationForm()
    return redirect('mojo:index')


@login_required(login_url='mojo:welcome')
def trip(request, trip_id):

    trip = get_object_or_404(Trip, uuid=trip_id)
    activities = trip.userenteredactivity_set.all()
    model_suggestions = ModelTripActivity.objects.filter(trip=trip).exclude(trip_locations__status='rejected')
    # Trip plan items visible to all participants
    plan_items = TripPlanItem.objects.filter(trip=trip).select_related('activity')
    planned_activity_ids = set(plan_items.values_list('activity__id', flat=True))
    # Determine which model suggestions are saved by the current user
    saved_place_ids = list(
        TripActivityDetails.objects.filter(
            trip=trip,
            user=request.user,
            status='saved'
        ).values_list('place_id', flat=True)
    )
    # Determine which suggestions the user has responded to (any status)
    responded_place_ids = list(
        TripActivityDetails.objects.filter(
            trip=trip,
            user=request.user,
        ).values_list('place_id', flat=True)
    )
    # Compute which suggestions have no status from the current user
    suggestion_ids = list(model_suggestions.values_list('id', flat=True))
    no_status_place_ids = [sid for sid in suggestion_ids if sid not in responded_place_ids]
    activity_comments = {}
    for activity in model_suggestions:
        comments = TripActivityComment.objects.filter(trip_activity=activity)
        activity_comments[activity.id] = comments
    participant = TripParticipant.objects.filter(trip=trip)
    # Determine editor permissions: owner or contributor
    is_owner = trip.created_by == request.user
    is_contributor = TripParticipant.objects.filter(trip=trip, user=request.user, role='contributor').exists()
    is_owner_role = TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
    is_editor = is_owner or is_contributor or is_owner_role
    can_manage_participants = is_owner or is_owner_role

    return render(request, 'trip.html', {'trip': trip,
                                         'activities': activities,
                                         'model_suggestions': model_suggestions,
                                         'activity_comments': activity_comments,
                                         'participant': participant,
                                         'plan_items': plan_items,
                                         'planned_activity_ids': planned_activity_ids,
                                         'is_editor': is_editor,
                                         'can_manage_participants': can_manage_participants,
                                         'saved_place_ids': saved_place_ids,
                                         'no_status_place_ids': no_status_place_ids})


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
  activities = UserEnteredActivity.objects.filter(trip=trip).values_list('activity_name', flat=True)
  client = OpenAI()
  serialized_start_date = trip.start_date.strftime("%Y-%m-%d")
  serialized_end_date = trip.end_date.strftime("%Y-%m-%d")
  serialized_activities = json.dumps(list(activities))
  rejected_model_suggestions = ModelTripActivity.objects.filter(trip=trip, trip_locations__status='rejected').values_list('location_string', flat=True)
  saved_model_suggestions = ModelTripActivity.objects.filter(trip=trip, trip_locations__status='saved').values_list('location_string', flat=True)
  rejected_model_suggestions_serialized = json.dumps(list(rejected_model_suggestions))
  saved_model_suggestions_serialized = json.dumps(list(saved_model_suggestions))

  response = client.responses.create(
    prompt={
        "id": "pmpt_689e839191808196aee8f2537e3c63770d2c7182b27d433c",
        "version": "5",
        "variables": {
          "travel_destination": trip.destination_city,
          "trip_start_date": serialized_start_date,
          "trip_end_date": serialized_end_date,
          "activities": serialized_activities,
          "saved_model_suggestions": saved_model_suggestions_serialized,
          "rejected_model_suggestions": rejected_model_suggestions_serialized
      }
    }
)
  print(response.output[0].content[0].text)
  activities_list = json.loads(response.output[0].content[0].text)

# If there are already suggestions for this trip, delete them
  ModelTripActivity.objects.filter(trip=trip).exclude(trip_locations__status__in=['rejected', 'saved']).delete()

  for activity in activities_list:
    ModelTripActivity.objects.create(
      trip=trip,
      name=activity['activity_name'],
      description=activity['activity_description'],
      location_string=activity['place'],
      url=activity['place_url']
    )

  return redirect('mojo:trip', trip_id)

@login_required(login_url='mojo:login')
def heart_model_suggestion(request, model_trip_activity_id):
  model_trip_activity = ModelTripActivity.objects.get(id=model_trip_activity_id)
  # Check if a TripActivityDetails exists for this user/trip/place
  trip_activity_detail = TripActivityDetails.objects.filter(
      trip=model_trip_activity.trip,
      place=model_trip_activity,
      user=request.user,
  ).first()

  if trip_activity_detail is None:
    # None exists: create with 'saved'
    TripActivityDetails.objects.create(
        trip=model_trip_activity.trip,
        place=model_trip_activity,
        user=request.user,
        status='saved'
    )
    print(f"Created new TripActivityDetail object (saved) for trip {model_trip_activity.trip.uuid}")
  elif getattr(trip_activity_detail, 'status', None) == 'rejected':
    # Exists but was rejected: update to 'saved'
    trip_activity_detail.status = 'saved'
    trip_activity_detail.save(update_fields=['status'])
    print(f"Updated TripActivityDetail status to 'saved' for trip {model_trip_activity.trip.uuid}")
  else:
    # Exists and not rejected (likely already saved) -> no-op
    print(f"TripActivityDetail already exists with status '{trip_activity_detail.status}' for trip {model_trip_activity.trip.uuid}")
  return redirect('mojo:trip', trip_id=model_trip_activity.trip.uuid)

@login_required(login_url='mojo:login')
def reject_model_suggestion(request, model_trip_activity_id):
  model_trip_activity = ModelTripActivity.objects.get(id=model_trip_activity_id)
  trip_activity_detail, created = TripActivityDetails.objects.get_or_create(
      trip=model_trip_activity.trip,
      place=model_trip_activity,
      user=request.user,
      defaults={'status': 'rejected'}
  )

  if created:
    print(f"Created new TripActivityDetail object for trip {model_trip_activity.trip.uuid}")
  else:
    print(f"TripActivityDetail object already exists for trip {model_trip_activity.trip.uuid}")
  return redirect('mojo:trip', trip_id=model_trip_activity.trip.uuid)


@login_required(login_url='mojo:login')
def share_trip(request, trip_id):
  """
  Share a trip with another user.

  This function takes a POST request containing the email address of the user
  to share the trip with. If the user exists, it creates a new TripParticipant
  object, otherwise it creates a new SharedTrip object. After successful creation,
  it redirects the user back to the index page.

  Parameters:
  request (HttpRequest): The POST request containing the email address of the user to share the trip with.
  trip_id (str): The UUID of the trip to share.

  Returns:
  HttpResponse: A redirect to the index page.

  """

  trip = Trip.objects.get(uuid=trip_id)
  email = request.POST.get('email')
  try:
    user = CustomUser.objects.get(email=email)
    trip_participant, created = TripParticipant.objects.get_or_create(
      trip=trip,
      user=user,
      role="contributor"
    )

  except CustomUser.DoesNotExist:
    shared_trip, created = SharedTrip.objects.get_or_create(
        trip=trip,
        shared_with=email,
    )
    if created:
      print(f"Created new SharedTrip object for trip {trip.uuid}")
    else:
      print(f"SharedTrip object already exists for trip {trip.uuid}")

  # Redirect back to the page the share was initiated from
  next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or ''
  if isinstance(next_url, str) and next_url.startswith('/'):
    return redirect(next_url)
  return redirect('mojo:index')

@login_required(login_url='mojo:login')
def add_comment(request, trip_activity_id):
  trip_activity = ModelTripActivity.objects.get(id=trip_activity_id)
  add_comment = request.POST.get('comment')
  TripActivityComment.objects.create(trip_activity=trip_activity,
                                     comment=add_comment, created_by=request.user)
  return redirect('mojo:trip', trip_id=trip_activity.trip.uuid)


def delete_user_entered_activity(request, user_generated_trip_activity_id):
  user_entered_trip_activity = UserEnteredActivity.objects.get(id=user_generated_trip_activity_id)
  generated_trip_activity = user_entered_trip_activity.trip
  user_entered_trip_activity.delete()
  return redirect('mojo:trip', trip_id=generated_trip_activity.uuid)


def welcome(request):
  return render(request, 'welcome.html')


@login_required(login_url='mojo:login')
def delete_trip(request, trip_id):
  """
  Delete a trip owned by the current user. POST only.
  """
  if request.method != 'POST':
    return redirect('mojo:index')

  trip = get_object_or_404(Trip, uuid=trip_id)

  # Only the owner/creator may delete the trip
  is_owner = (trip.created_by == request.user) or TripParticipant.objects.filter(
      trip=trip, user=request.user, role='owner'
  ).exists()

  if not is_owner:
    return redirect('mojo:index')

  trip.delete()
  return redirect('mojo:index')


@login_required(login_url='mojo:login')
def add_plan_item(request, trip_id, activity_id):
  """
  Add a suggested activity to the Trip Plan. POST only.
  Only owners or contributors may add items. Viewers are read-only.
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)


  # Permission check: owner or contributor (or participant with role owner)
  is_owner = trip.created_by == request.user
  is_contributor = TripParticipant.objects.filter(trip=trip, user=request.user, role='contributor').exists()
  is_owner_role = TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
  if not (is_owner or is_contributor or is_owner_role):
    return redirect('mojo:trip', trip_id=trip.uuid)
  # Determine next position
  max_pos = TripPlanItem.objects.filter(trip=trip).aggregate(Max('position')).get('position__max') or 0
  activity = get_object_or_404(ModelTripActivity, id=activity_id, trip=trip)
  TripPlanItem.objects.get_or_create(
      trip=trip,
      activity=activity,
      defaults={'added_by': request.user, 'position': max_pos + 1}
  )
  # Mark this suggestion as saved for the trip (and current user)
  TripActivityDetails.objects.update_or_create(
      trip=trip,
      place=activity,
      defaults={'status': 'saved', 'user': request.user}
  )
  return redirect('mojo:trip', trip_id=trip.uuid)



@login_required(login_url='mojo:login')
def delete_plan_item(request, trip_id, plan_item_id):
  """
  Delete a TripPlanItem. POST only.
  Only owners or contributors may delete items.
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)

  is_owner = trip.created_by == request.user
  is_contributor = TripParticipant.objects.filter(trip=trip, user=request.user, role='contributor').exists()
  is_owner_role = TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
  if not (is_owner or is_contributor or is_owner_role):
    return redirect('mojo:trip', trip_id=trip.uuid)

  plan_item = get_object_or_404(TripPlanItem, id=plan_item_id, trip=trip)
  plan_item.delete()
  return redirect('mojo:trip', trip_id=trip.uuid)


@login_required(login_url='mojo:login')
def update_plan_item(request, trip_id, plan_item_id):
  """
  Update scheduled_date/time for a TripPlanItem. POST only.
  Only owners or contributors may update items.
  Expects fields: scheduled_date (YYYY-MM-DD or empty), scheduled_time (HH:MM or empty)
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)

  is_owner = trip.created_by == request.user
  is_contributor = TripParticipant.objects.filter(trip=trip, user=request.user, role='contributor').exists()
  is_owner_role = TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
  if not (is_owner or is_contributor or is_owner_role):
    return redirect('mojo:trip', trip_id=trip.uuid)

  plan_item = get_object_or_404(TripPlanItem, id=plan_item_id, trip=trip)
  sched_date = request.POST.get('scheduled_date') or None
  sched_time = request.POST.get('scheduled_time') or None
  # Assign parsed values; let Django handle parsing via form fields if valid
  plan_item.scheduled_date = sched_date if sched_date else None
  plan_item.scheduled_time = sched_time if sched_time else None
  plan_item.save(update_fields=['scheduled_date', 'scheduled_time'])
  return redirect('mojo:trip', trip_id=trip.uuid)


@login_required(login_url='mojo:login')
def move_plan_item(request, trip_id, plan_item_id):
  """
  Move a TripPlanItem up or down within a trip's plan.
  POST only with field 'direction' in {'up','down'}.
  Only owners or contributors may reorder.
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)

  is_owner = trip.created_by == request.user
  is_contributor = TripParticipant.objects.filter(trip=trip, user=request.user, role='contributor').exists()
  is_owner_role = TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
  if not (is_owner or is_contributor or is_owner_role):
    return redirect('mojo:trip', trip_id=trip.uuid)

  plan_item = get_object_or_404(TripPlanItem, id=plan_item_id, trip=trip)
  direction = request.POST.get('direction')
  if direction not in ('up', 'down'):
    return redirect('mojo:trip', trip_id=trip.uuid)

  if direction == 'up':
    neighbor = TripPlanItem.objects.filter(trip=trip, position__lt=plan_item.position).order_by('-position').first()
  else:
    neighbor = TripPlanItem.objects.filter(trip=trip, position__gt=plan_item.position).order_by('position').first()

  if neighbor:
    plan_item.position, neighbor.position = neighbor.position, plan_item.position
    plan_item.save(update_fields=['position'])
    neighbor.save(update_fields=['position'])
  return redirect('mojo:trip', trip_id=trip.uuid)


@login_required(login_url='mojo:login')
def update_participant_role(request, trip_id, participant_id):
  """
  Update a participant's role. Owner-only action. POST only.
  Prevent demoting the last owner on the trip.
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)

  # Only owners may manage roles
  is_owner = (trip.created_by == request.user) or TripParticipant.objects.filter(trip=trip, user=request.user, role='owner').exists()
  if not is_owner:
    return redirect('mojo:trip', trip_id=trip.uuid)

  tp = get_object_or_404(TripParticipant, id=participant_id, trip=trip)
  new_role = request.POST.get('role')
  if new_role not in ('owner', 'contributor', 'viewer'):
    return redirect('mojo:trip', trip_id=trip.uuid)

  # Prevent removing the last owner
  if tp.role == 'owner' and new_role != 'owner':
    owner_count = TripParticipant.objects.filter(trip=trip, role='owner').count()
    if owner_count <= 1:
      return redirect('mojo:trip', trip_id=trip.uuid)

  tp.role = new_role
  tp.save(update_fields=['role'])
  return redirect('mojo:trip', trip_id=trip.uuid)


@login_required(login_url='mojo:login')
def add_plan_item_comment(request, trip_id, plan_item_id):
  """
  Add a comment to a TripPlanItem. POST only.
  Any participant (owner/contributor/viewer) may comment.
  """
  trip = get_object_or_404(Trip, uuid=trip_id)
  if request.method != 'POST':
    return redirect('mojo:trip', trip_id=trip.uuid)

  # Ensure the user is related to the trip (creator or participant)
  is_related = (trip.created_by == request.user) or TripParticipant.objects.filter(trip=trip, user=request.user).exists()
  if not is_related:
    return redirect('mojo:trip', trip_id=trip.uuid)

  plan_item = get_object_or_404(TripPlanItem, id=plan_item_id, trip=trip)
  text = (request.POST.get('comment') or '').strip()
  if text:
    TripActivityComment.objects.create(
      trip_activity=plan_item.activity,
      plan_item=plan_item,
      comment=text,
      created_by=request.user,
    )
  return redirect('mojo:trip', trip_id=trip.uuid)