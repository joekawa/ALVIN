from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid


STATES = (
    ('', 'Select State'),
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming")
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, city, state, dob, password=None):
        """
        Creates and saves a User with the given email, city, state, and
        date of birth. Optionally takes a password argument.

        Raises ValueError if email is not present.

        Returns the User object.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            state = state,
            city = city,
            dob = dob
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates a superuser with the given email and password.

        The superuser's email field will be set to the given email address,
        and the password will be set to the given password. The user's
        is_admin field will be set to True, and the user will be saved to
        the database.

        :param email: The email address of the superuser.
        :param password: The password for the superuser.
        :return: The newly created superuser.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    __name__ = 'CustomUser'
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    dob = models.DateField()
    is_admin = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['city','state','zip_code','dob']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


 
class Trip(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_name = models.CharField(max_length=255)
    destination_city = models.CharField(max_length=255)
    destination_state = models.CharField(max_length=255, default="NA")
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        """
        Returns the string representation of the object, which is the name of the trip
        followed by the username of the user who created the trip in parentheses.

        Example:
            "Trip to Disneyland (john)"
        """
        return f"{self.trip_name}"



class TripParticipant(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("contributor", "Contributor"),  # can add/remove activities
        ("viewer", "Viewer"),  # read-only
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES,
                            default="contributor")
    invited_at = models.DateTimeField(auto_now_add=True)
    class Meta:
            unique_together = ("trip", "user")

    def __str__(self):
        return f"{self.user} ({self.role}) in {self.trip.trip_name}"



#* THIS IS THE ACTIVITY A USER WANTS TO DO ON THE TRIP
class UserEnteredActivity(models.Model):
    activity_name = models.CharField(max_length=255)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

#* THIS IS THE ACTIVITY THE MODEL SUGGESTED
class ModelTripActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    location_string = models.CharField(max_length=255,
                                       help_text="Raw GPT-provided location string")
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=50, default="chatgpt")  # or user_input, api, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["latitude", "longitude"]),  # supports geo queries
        ]

    def __str__(self):
        return self.name


class TripPlanItem(models.Model):
    """
    A planned item for a trip, created from a model suggestion.
    Visible to all participants. Only owners/contributors can add.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE, related_name='plan_items')
    activity = models.ForeignKey('ModelTripActivity', on_delete=models.CASCADE, related_name='planned_in_trips')
    added_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='added_plan_items')
    added_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        unique_together = ("trip", "activity")
        ordering = ["position", "added_at"]

    def __str__(self):
        return f"PlanItem({self.trip.trip_name}: {self.activity.name})"

#* THIS IS HOW THE USER REACTED TO THE MODEL SUGGESTION
class TripActivityDetails(models.Model):
    STATUS_CHOICES = [
        ("saved", "Saved"),
        ("rejected", "Rejected"),
        ('blank', 'Blank'), #indicates no response
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip")
    place = models.ForeignKey(ModelTripActivity, on_delete=models.CASCADE, related_name="trip_locations")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="blank")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


    class Meta:
        unique_together = ("trip", "place")  # prevents duplicates

    def __str__(self):
        return f"{self.place.name} for {self.trip.trip_name}"


class TripActivityComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_activity = models.ForeignKey(ModelTripActivity, on_delete=models.CASCADE)
    # Optional link to a specific planned item
    plan_item = models.ForeignKey('TripPlanItem', on_delete=models.CASCADE, null=True, blank=True, related_name='plan_comments')
    comment = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_by.username}: {self.comment}"


#* THIS STORES A SHARED TRIP.  WHEN A USER SHARES A TRIP WITH ANOTHER EMAIL
#* IT'S LOGGED IN SharedTrip.  IF THE EMAIL DOESN'T EXIST IN THE DB,
#* IT'S LOGGED IN SharedTrip AND THEN WILL BE SHARED TO THE EMAIL WHEN THE USER
#* SIGNS UP
class SharedTrip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    shared_with = models.EmailField()
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("trip", "shared_with")

    def __str__(self):
        return f"{self.trip.trip_name} shared with {self.shared_with} at {self.shared_at}"