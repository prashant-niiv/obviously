from rest_framework import serializers

from profiles.models import Person


class PersonSerializer(serializers.ModelSerializer):
    """Serializer for full Person details."""
    age = serializers.ReadOnlyField()  # Read-only since it's calculated

    class Meta:
        model = Person
        fields = '__all__'  # Includes all model fields
        extra_kwargs = {
            "embedding": {"required": False}  # Not required during create/update
        }


class PersonSearchSerializer(serializers.ModelSerializer):
    """Serializer for searching/filtering Person data with limited fields."""
    age = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'age']
