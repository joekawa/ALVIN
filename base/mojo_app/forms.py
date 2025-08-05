from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, CharField, DateField
from django.forms import ModelForm ,TextInput, PasswordInput, EmailInput, Select
from .models import CustomUser, STATES
from django.contrib.auth import *

class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True,
                             widget=EmailInput(
                                attrs={'class': "form-control",
                                       'placeholder': "Email"}))
    password1 = CharField(max_length=30, required=True,
                               widget=PasswordInput(
                                     attrs={'class': "form-control",
                                            'placeholder': "Enter Password"}))
    password2 = CharField(max_length=30, required=True,
                                widget=PasswordInput(
                                     attrs={'class': "form-control",
                                            'placeholder': "Repeat Password"}))
    city = CharField(max_length=50, required=False,
                           widget=TextInput(
                               attrs={'class': "form-control",
                                      'placeholder': "City"}))
    state = CharField(max_length=50, required=False,
                            widget=Select(attrs={'class': ("form-select")},
                                          choices=STATES))
    zip_code = CharField(max_length=10, required=False,
                               widget=TextInput(
                                   attrs={'class': "form-control",
                                          'placeholder': "Zip Code"}))
    dob = DateField(required=False,
                          widget=TextInput(
                              attrs={'class': "form-control",
                                     'placeholder': "Date of Birth"}))

    class Meta:
        model = CustomUser
        fields = ('email', 'city', 'state', 'zip_code', 'dob',
                  'password1', 'password2')