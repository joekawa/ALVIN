from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

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
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    dob = models.DateField()
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['city','state','zip_code','dob']

    def __str__(self):
        """
        Returns the string representation of the user, which is the user's email address.
        """
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Simple property that returns whether the user has the specified permission or not.

        Since we don't have any permission system in place, we just return True.
        """
        return True

    def has_module_perms(self, app_label):
        """
        Simple property that returns whether the user has permissions to view the app or not.

        Since we don't have any permission system in place, we just return True.
        """
        return True

    @property
    def is_staff(self):
        """
        Simple property that returns whether the user is a staff member or not.

        We use `is_admin` as the flag for this property, since we don't have
        a separate field for it. This is okay since we don't need to treat
        staff members differently than admins in any way.
        """
        return self.is_admin


class Trip(models.Model):
    trip_name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.trip_name
