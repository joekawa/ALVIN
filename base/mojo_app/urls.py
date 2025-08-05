from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'mojo'

urlpatterns = [
  path('', views.index, name='index'),
  path('login', views.login_view, name='login'),
  path('signup', views.signup, name='signup'),
  path('logout/', LogoutView.as_view(next_page='mojo:login'), name='logout'),
]

