import unittest
from django.test import TestCase
from .models import Trip

class TripTestCase(TestCase):
    def test_trip_creation(self):
        trip = Trip.objects.create(
            name='Test Trip',
            description='This is a test trip',
            start_date='2022-01-01',
            end_date='2022-01-31',
            destination='Test Destination'
        )
        self.assertEqual(trip.name, 'Test Trip')
        self.assertEqual(trip.description, 'This is a test trip')
        self.assertEqual(trip.start_date, '2022-01-01')
        self.assertEqual(trip.end_date, '2022-01-31')
        self.assertEqual(trip.destination, 'Test Destination')

    def test_trip_update(self):
        trip = Trip.objects.create(
            name='Test Trip',
            description='This is a test trip',
            start_date='2022-01-01',
            end_date='2022-01-31',
            destination='Test Destination'
        )
        trip.name = 'Updated Trip'
        trip.description = 'This is an updated test trip'
        trip.start_date = '2022-02-01'
        trip.end_date = '2022-02-28'
        trip.destination = 'Updated Destination'
        trip.save()
        self.assertEqual(trip.name, 'Updated Trip')
        self.assertEqual(trip.description, 'This is an updated test trip')
        self.assertEqual(trip.start_date, '2022-02-01')
        self.assertEqual(trip.end_date, '2022-02-28')
        self.assertEqual(trip.destination, 'Updated Destination')

    def test_trip_delete(self):
        trip = Trip.objects.create(
            name='Test Trip',
            description='This is a test trip',
            start_date='2022-01-01',
            end_date='2022-01-31',
            destination='Test Destination'
        )
        trip.delete()
        self.assertEqual(Trip.objects.count(), 0)


class ActivityTestCase(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            name='Test Trip',
            description='This is a test trip',
            start_date='2022-01-01',
            end_date='2022-01-31',
            destination='Test Destination'
        )

    def test_activity_creation(self):
        activity = Activity.objects.create(
            name='Test Activity',
            trip=self.trip
        )
        self.assertEqual(activity.name, 'Test Activity')
        self.assertEqual(activity.trip, self.trip)

    def test_activity_update(self):
        activity = Activity.objects.create(
            name='Test Activity',
            trip=self.trip
        )
        activity.name = 'Updated Activity'
        activity.save()
        self.assertEqual(activity.name, 'Updated Activity')
        self.assertEqual(activity.trip, self.trip)

    def test_activity_delete(self):
        activity = Activity.objects.create(
            name='Test Activity',
            trip=self.trip
        )
        activity.delete()
        self.assertEqual(Activity.objects.count(), 0)

    def test_activity_trip_relationship(self):
        activity = Activity.objects.create(
            name='Test Activity',
            trip=self.trip
        )
        self.assertEqual(activity.trip, self.trip)
        self.assertIn(activity, self.trip.activity_set.all())


class ModelSuggestionsTestCase(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            name='Test Trip',
            description='This is a test trip',
            start_date='2022-01-01',
            end_date='2022-01-31',
            destination='Test Destination'
        )

    def test_model_suggestions_creation(self):
        model_suggestions = ModelSuggestions.objects.create(
            trip=self.trip,
            suggestion='Test Suggestion'
        )
        self.assertEqual(model_suggestions.trip, self.trip)
        self.assertEqual(model_suggestions.suggestion, 'Test Suggestion')

    def test_model_suggestions_update(self):
        model_suggestions = ModelSuggestions.objects.create(
            trip=self.trip,
            suggestion='Test Suggestion'
        )
        model_suggestions.suggestion = 'Updated Suggestion'
        model_suggestions.save()
        self.assertEqual(model_suggestions.suggestion, 'Updated Suggestion')
        self.assertEqual(model_suggestions.trip, self.trip)

    def test_model_suggestions_delete(self):
        model_suggestions = ModelSuggestions.objects.create(
            trip=self.trip,
            suggestion='Test Suggestion'
        )
        model_suggestions.delete()
        self.assertEqual(ModelSuggestions.objects.count(), 0)

    def test_model_suggestions_trip_relationship(self):
        model_suggestions = ModelSuggestions.objects.create(
            trip=self.trip,
            suggestion='Test Suggestion'
        )
        self.assertEqual(model_suggestions.trip, self.trip)
        self.assertIn(model_suggestions, self.trip.modelsuggestions_set.all())