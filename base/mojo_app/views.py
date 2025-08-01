from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.

def index(request):
  """
  The main entry point of the app. This function renders the
  base HTML template for the app.
  """

  return render(request, 'mojo_app/index.html')

def login(request):
  """
  Renders the login page, which contains a form for users to
  submit their email and password.
  """
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username)
    print(password)
    return redirect('index')

  return render(request, 'mojo_app/login.html')


def signup(request):
  """
  Renders the signup page, which contains a form for
  users to submit their name, email, password, confirm password,
  zip code, and date of birth.
  """
  return render(request, 'mojo_app/signup.html')
