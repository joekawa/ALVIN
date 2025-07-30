from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
  """
  The main entry point of the app. This function renders the
  base HTML template for the app.
  """

  return HttpResponse("Hello, world. You're at the mojo index.")
