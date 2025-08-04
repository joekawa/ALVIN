from django.urls import path

from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('log_in', views.log_in, name='log_in'),
  path('signup', views.signup, name='signup'),
  path('create_user', views.create_user, name='create_user'),
]

