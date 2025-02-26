from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from profiles.models import Person


class PersonAdmin(UserAdmin):
    model = Person

    # Fields displayed in the list view
    list_display = ("username", "email", "phone", "date_of_birth", "role", "is_staff", "created_at", "updated_at")

    # Fields used for searching
    search_fields = ("username", "email", "phone", "role")

    # Fields used for filtering
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    # How fields are grouped when editing a user
    fieldsets = (
        ("Personal Info", {"fields": ("first_name", "last_name",
         "username", "email", "phone", "date_of_birth", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone", "date_of_birth", "password1", "password2"),
        }),
    )

    readonly_fields = ("created_at", "updated_at")  # Prevent editing these fields manually


# Register the Person model with the custom admin class
admin.site.register(Person, PersonAdmin)
