from django.db import models


# Define choices using Django's built-in TextChoices class
class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    GUEST = "guest", "Guest"
