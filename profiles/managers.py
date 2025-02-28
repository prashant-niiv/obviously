from django.contrib.auth.models import BaseUserManager
from django.utils.timezone import now


class PersonManager(BaseUserManager):
    """
    Custom manager for the Person model to add additional query methods.
    """
    def create_user(self, username, email, phone, date_of_birth, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)  # Default role set to ADMIN
        return self.create_user(username, email, phone, date_of_birth, password, **extra_fields)

    def get_users_by_role(self, role):
        """Retrieve users by role."""
        return self.filter(role=role)

    def get_recent_users(self, days=7):
        """Retrieve users created within the last `days`."""
        time_threshold = now() - timedelta(days=days)
        return self.filter(created_at__gte=time_threshold)
