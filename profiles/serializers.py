from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from profiles.models import Person


class PersonSerializer(serializers.ModelSerializer):
    """Serializer for full Person details."""
    age = serializers.ReadOnlyField()  # Read-only as it's calculated

    class Meta:
        model = Person
        exclude = ['embedding']  # Exclude embedding field from API response as it's for internal use only
        extra_kwargs = {
            'password': {'write_only': True},  # Make password write-only
            'embedding': {'required': False}  # Not required during create/update
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        return super().create(validated_data)


class PersonSearchSerializer(serializers.ModelSerializer):
    """Serializer for searching/filtering Person data with limited fields."""
    age = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'age']
