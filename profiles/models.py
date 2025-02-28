import json
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from profiles.choices import Role
from profiles.managers import PersonManager
from profiles.utils import get_embedding_model
from profiles.validators import validate_date_of_birth


# Create your models here.
class Person(AbstractUser):
    """
    This model extends Django's AbstractUser to define user roles and personal details.
    """
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(validators=[validate_date_of_birth])
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    embedding = models.TextField()  # Stores vector embeddings in text format
    created_at = models.DateTimeField(auto_now_add=True)  # Set only once when created
    updated_at = models.DateTimeField(auto_now=True)  # Updates every time the record changes

    objects = PersonManager()  # Custom manager for the Person model

    REQUIRED_FIELDS = ["phone", "date_of_birth"]  # Fields prompted when creating a superuser

    class Meta:
        verbose_name = "Person"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        """
        Generate and store the embedding when saving the Person instance.
        """
        add_embedding = True

        update_fields = set(kwargs["update_fields"]) if "update_fields" in kwargs else None
        if self.pk and update_fields and {"first_name", "last_name"}.isdisjoint(update_fields):
            add_embedding = False  # Skip embedding update if name fields haven't changed

        if add_embedding:
            full_name = f"{self.first_name} {self.last_name}".strip()
            try:
                embedding_model = get_embedding_model()
                embedding_vector = embedding_model.encode(full_name).tolist()
                self.embedding = json.dumps(embedding_vector)  # Store as JSON string
            except Exception:
                self.embedding = json.dumps([])  # Store empty embedding in case of failure
        super().save(*args, **kwargs)

    @property
    def age(self):
        """
        Calculate age based on date_of_birth.
        """
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
