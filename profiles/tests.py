from datetime import date

from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles.choices import Role
from profiles.models import Person


class PersonViewSetTests(APITestCase):
    def setUp(self):
        """Set up test data with different user roles."""

        # Create an admin user
        self.admin_user = Person.objects.create(
            username="admin",
            first_name="Prince",
            last_name="Adam",
            password="admin123",
            email="admin@example.com",
            phone="0123456789",
            date_of_birth=date(1990, 2, 25),
            role=Role.ADMIN
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create a guest user
        self.guest_user = Person.objects.create(
            username="guest",
            first_name="Scarlet",
            last_name="Gust",
            password="guest123",
            email="guest@example.com",
            phone="9876543210",
            date_of_birth=date(1995, 9, 10),
            role=Role.GUEST
        )
        self.guest_token = Token.objects.create(user=self.guest_user)

        # Create a normal user
        self.person1 = Person.objects.create(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
            date_of_birth=date(1992, 5, 15),
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
        """Admin should be able to view all persons."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(reverse("profiles:person-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_guest_cannot_list_persons(self):
        """Guest users should not have permission to view persons."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        response = self.client.get(reverse("profiles:person-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_person(self):
        """Admin should be able to create a new person."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
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
        response = self.client.post(reverse("profiles:person-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_guest_cannot_create_person(self):
        """Guest users should not be able to create a person."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
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
        response = self.client.post(reverse("profiles:person-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_person_search_by_first_name(self):
        """Searching persons by first name should return correct results."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-search") + "?first_name=John"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "John")

    def test_person_search_by_age(self):
        """Searching persons by age should return correct results."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        age = date.today().year - 1990
        url = reverse("profiles:person-search") + f"?age={age}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "Prince")

    def test_invalid_age_in_search(self):
        """Providing an invalid age should return a 400 error."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-search") + "?age=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Age must be an integer")

    def test_vector_search_by_valid_name(self):
        """Vector search should return correct results with a valid name."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=John"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_vector_search_by_missing_name(self):
        """Vector search should return 400 error if name is not provided."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Provide at least one name")

    def test_vector_search_no_results(self):
        """Vector search should return 200 with a no results message when no matches are found."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=Unknown"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "No similar persons found")

    def test_vector_search_by_partial_name(self):
        """Vector search should work with partial names."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=Ja"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)


class LoginViewTests(APITestCase):
    def setUp(self):
        """Set up a test user for authentication tests."""
        self.user = Person.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword",
            email="test@example.com",
            phone="1133557799",
            date_of_birth=date(1996, 12, 23),
            role=Role.ADMIN
        )
        self.url = reverse("profiles:login")

    def test_login_successful(self):
        """A user with correct credentials should receive a token."""
        response = self.client.post(
            self.url, {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_unsuccessful(self):
        """A user with incorrect credentials should get a 400 error."""
        response = self.client.post(
            self.url, {"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid credentials")
