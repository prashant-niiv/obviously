from datetime import date, timedelta

from django.contrib.auth import authenticate
from django.db.models import Q

from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from profiles.models import Person
from profiles.pagination import StandardResultsSetPagination
from profiles.permissions import IsAdminOrGuestUser, IsAdminUser
from profiles.serializers import PersonSearchSerializer, PersonSerializer


class LoginView(views.APIView):
    """
    API endpoint to authenticate a user and return an auth token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admin to perform CRUD operations on Person entities.
    """
    queryset = Person.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["get"], permission_classes=[IsAdminOrGuestUser])
    def search(self, request):
        """
        Filter persons by first_name, last_name (partial match) and/or age.
        """
        first_name = request.query_params.get('first_name', '')
        last_name = request.query_params.get('last_name', '')
        age = request.query_params.get('age', None)

        filters = Q()

        if first_name:
            filters |= Q(first_name__icontains=first_name)
        if last_name:
            filters |= Q(last_name__icontains=last_name)

        if age:
            try:
                age = int(age)
                today = date.today()
                dob_start = date(today.year - age - 1, today.month, today.day) + timedelta(days=1)
                dob_end = date(today.year - age, today.month, today.day)
                filters &= Q(date_of_birth__range=(dob_start, dob_end))
            except ValueError:
                return Response({'error': 'Age must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        persons = Person.objects.filter(filters).only("first_name", "last_name", "email", "phone", "date_of_birth")
        serializer = PersonSearchSerializer(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
