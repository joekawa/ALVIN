from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, CharField, DateField
from django.forms import ModelForm ,TextInput, PasswordInput, DateInput, EmailInput, Select
from .models import CustomUser, STATES, Trip, UserEnteredActivity
from django import forms
from django.contrib.auth import *
import datetime

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




class TripCreationForm(ModelForm):
    trip_name = CharField(label="Trip Name",max_length=30, required=True,
                               widget=TextInput(
                                     attrs={'class': "form-control",
                                            'placeholder': "Trip Name",
                                            'name': "trip_name"}))
    destination = CharField(label="Destination",max_length=30, required=True,
                               widget=TextInput(
                                     attrs={'class': "form-control",
                                            'placeholder': "Enter Destination",
                                            'id': "destination-input"}))
    start_date = DateField(label="Start Date",required=True,
                               widget=DateInput(
                                     attrs={'class': "form-control",
                                            'type': "date",
                                            'name': "start_date"}))
    end_date = DateField(label="End Date", required=True,
                               widget=DateInput(
                                     attrs={'class': "form-control",
                                            'placeholder': "Enter End Date",
                                            'type': "date",
                                            'name': "end_date"}))


    class Meta:
        model = Trip
        fields = ('trip_name', 'start_date', 'end_date', 'destination')

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date < datetime.date.today():
            raise forms.ValidationError('Start date must be in the future')
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        start_date = self.cleaned_data['start_date']
        if end_date < start_date:
            raise forms.ValidationError('End date must be after start date')
        return end_date


class UserCreatedActivityForm(ModelForm):
    class Meta:
        model = UserEnteredActivity
        fields = ('activity_name',)


class ProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('city', 'state', 'zip_code', 'dob')