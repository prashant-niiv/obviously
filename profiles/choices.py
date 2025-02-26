from django.db import models


# Add your choices here.
class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    GUEST = "guest", "Guest"
