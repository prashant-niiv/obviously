from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from profiles.choices import Role


# Create your models here.
class Person(AbstractUser):
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)  # Set only once when created
    updated_at = models.DateTimeField(auto_now=True)  # Updates every time the record changes

    REQUIRED_FIELDS = ["phone", "date_of_birth"]  # Fields prompted when creating a superuser

    class Meta:
        verbose_name = "Person"

    @property
    def age(self):
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
