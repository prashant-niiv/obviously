from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import date, timedelta
from profiles.models import Person
from profiles.choices import Role

User = get_user_model()

class PersonViewSetTests(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin123", email="admin@example.com", role=Role.ADMIN
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create a guest user
        self.guest_user = User.objects.create_user(
            username="guest", password="guest123", email="guest@example.com", role=Role.GUEST
        )
        self.guest_token = Token.objects.create(user=self.guest_user)

        # Create a normal user
        self.person = Person.objects.create(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
            date_of_birth=date(1990, 5, 15),
            role=Role.GUEST
        )

        self.person2 = Person.objects.create(
            username="jane_doe",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="0987654321",
            date_of_birth=date(1985, 7, 20),
            role=Role.GUEST
        )

    def test_admin_can_list_persons(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(reverse("person-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_guest_cannot_list_persons(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        response = self.client.get(reverse("person-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_person(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        data = {
            "username": "new_user",
            "first_name": "New",
            "last_name": "User",
            "email": "new_user@example.com",
            "phone": "1112223333",
            "date_of_birth": "2000-01-01",
            "role": Role.GUEST,
            "password": "password123"
        }
        response = self.client.post(reverse("person-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_guest_cannot_create_person(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        data = {
            "username": "new_guest",
            "first_name": "Guest",
            "last_name": "User",
            "email": "guest_user@example.com",
            "phone": "1112223333",
            "date_of_birth": "2000-01-01",
            "role": Role.GUEST,
            "password": "password123"
        }
        response = self.client.post(reverse("person-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_person_search_by_first_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("person-search") + "?first_name=John"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "John")

    def test_person_search_by_age(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        age = date.today().year - 1990
        url = reverse("person-search") + f"?age={age}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "John")

    def test_invalid_age_in_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("person-search") + "?age=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Age must be an integer")


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("login")

    def test_login_successful(self):
        response = self.client.post(self.url, {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_unsuccessful(self):
        response = self.client.post(self.url, {"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid credentials")
