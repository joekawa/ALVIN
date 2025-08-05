from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from .models import CustomUser
# Create your views here.

def index(request):
  """
  The main entry point of the app. This function renders the
  base HTML template for the app.
  """

  return render(request, 'mojo_app/index.html', {'user': request.user})

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

  return render(request, 'mojo_app/login.html')


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
  return render(request, 'mojo_app/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')