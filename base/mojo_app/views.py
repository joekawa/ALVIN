from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import CustomUser
# Create your views here.

def index(request):
  """
  The main entry point of the app. This function renders the
  base HTML template for the app.
  """

  return render(request, 'mojo_app/index.html')

def log_in(request):
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

  return render(request, 'mojo_app/log_in.html')


def signup(request):
  """
  Renders the signup page, which contains a form for
  users to submit their name, email, password, confirm password,
  zip code, and date of birth.
  """
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    for f in form:
      print(f.name, f.value(), f.errors)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password1')
      zip_code = form.cleaned_data.get('zip_code')
      state = form.cleaned_data.get('state')
      city = form.cleaned_data.get('city')
      dob = form.cleaned_data.get('dob')
      user = CustomUser.objects.create(username=username,
                                      password=password,
                                      city=city,
                                      state=state,
                                      zip_code=zip_code,
                                      dob=dob
                                      )
      print("form is valid")
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      print("form is not valid")
  form = CustomUserCreationForm()
  return render(request, 'mojo_app/signup.html', {'form': form})


def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("form is valid")
            user = form.save()
            login(request, user)
            return redirect('')
    else:
        print("form is not valid")
        form = CustomUserCreationForm()
    return render(request, 'mojo_app/signup.html', {'form': form})