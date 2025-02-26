from rest_framework import serializers
from profiles.models import Person


class PersonSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()  # Read-only since it's calculated

    class Meta:
        model = Person
        fields = '__all__'


class PersonSearchSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'age']
