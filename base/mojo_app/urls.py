from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles import views

from . import views

app_name = 'mojo'

urlpatterns = [
  path('', views.index, name='index'),
  path('login/', views.login_view, name='login'),
  path('signup/', views.signup, name='signup'),
  path('profile/', views.profile, name='profile'),
  path('create_trip/', views.create_trip, name='create_trip'),
  path('logout/', LogoutView.as_view(next_page='mojo:login'), name='logout'),
  path('trip/<uuid:trip_id>/details/', views.trip, name='trip'),
  path('trip/<uuid:trip_id>/add_activity/', views.add_activity, name='add_activity'),
  path('trip/<uuid:trip_id>/trip_details/', views.generate_itinerary, name='generate_itinerary'),
  path('trip/<uuid:model_trip_activity_id>/heart/', views.heart_model_suggestion, name='heart_model_suggestion'),
  path('trip/<uuid:model_trip_activity_id>/reject/', views.reject_model_suggestion, name='reject_model_suggestion'),
]

