from rest_framework import serializers
from .models import *


class ModelTripActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTripActivity
        fields = [
            "id",
            "name",
            "activity_type",
            "description",
            "location_string",
            "address",
            "latitude",
            "longitude",
            "source",
            "created_at",
        ]


class TripActivityDetailsSerializer(serializers.ModelSerializer):
    location = ModelTripActivitySerializer(read_only=True)   # nested detail
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=ModelTripActivity.objects.all(), source="place", write_only=True
    )

    class Meta:
        model = TripActivityDetails
        fields = [
            "id",
            "trip",
            "location",
            "location_id",
            "notes",
            "status",
            "created_at",
        ]


class TripSerializer(serializers.ModelSerializer):
    trip_locations = ModelTripActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "user",
            "name",
            "start_date",
            "end_date",
            "created_at",
            "trip_locations",
        ]
        read_only_fields = ["user"]
