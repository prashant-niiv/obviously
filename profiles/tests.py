from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.timezone import now

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles.choices import Role
from profiles.models import Person


class PersonModelTests(APITestCase):
    """
    Test cases for the Person model, including validations and business logic.
    """
    def setUp(self):
        """
        Create a sample Person instance for testing.
        """
        self.person = Person.objects.create_user(
            username="jack-roy",
            email="jack@test.com",
            first_name="Jack",
            last_name="Roy",
            phone="1234567890",
            date_of_birth=date(1990, 5, 15),
            role=Role.ADMIN,
            password="testpassword",
        )
        self.token = Token.objects.create(user=self.person)

    def test_person_creation(self):
        """
        Test if the person instance is created correctly.
        """
        self.assertEqual(self.person.username, "jack-roy")
        self.assertEqual(self.person.email, "jack@test.com")
        self.assertEqual(self.person.first_name, "Jack")
        self.assertEqual(self.person.last_name, "Roy")
        self.assertEqual(self.person.phone, "1234567890")
        self.assertEqual(self.person.date_of_birth, date(1990, 5, 15))
        self.assertEqual(self.person.role, Role.ADMIN)
        self.assertTrue(self.person.check_password("testpassword"))

    def test_person_creation_without_email(self):
        """
        Test that creating a Person without an email raises a ValueError.
        """
        with self.assertRaises(ValueError) as context:
            Person.objects.create_user(
                username="no-email",
                email="",
                first_name="No",
                last_name="Email",
                phone="9876543210",
                date_of_birth=date(1998, 5, 25),
                role=Role.GUEST,
                password="noemailpassword",
            )
        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_str_representation(self):
        """
        Test the __str__ method of the Person model.
        """
        self.assertEqual(str(self.person), "Jack Roy")

    def test_age_calculation(self):
        """
        Test the age property.
        """
        today = date.today()
        expected_age = today.year - 1990 - ((today.month, today.day) < (5, 15))
        self.assertEqual(self.person.age, expected_age)

    def test_date_of_birth_too_old(self):
        """
        Test that a date of birth before 1901 raises a validation error.
        """
        with self.assertRaises(ValidationError):
            person = Person(
                username="old-user",
                password="oupassword",
                email="old@user.com",
                phone="1234567890",
                date_of_birth=date(1899, 12, 31),
                role=Role.GUEST,
            )
            person.full_clean()  # Triggers model validation

    def test_future_date_of_birth(self):
        """
        Test that a future date of birth raises a validation error.
        """
        with self.assertRaises(ValidationError):
            person = Person(
                username="future-user",
                password="fupassword",
                email="future@user.com",
                phone="1234567890",
                date_of_birth=now().date() + timedelta(days=1),
                role=Role.GUEST,
            )
            person.full_clean()  # Triggers model validation

    def test_token_generation(self):
        """
        Test if the authentication token is created for the user.
        """
        self.assertIsNotNone(self.token)
        self.assertEqual(self.token.user, self.person)

    def test_person_delete(self):
        """
        Test that a Person object can be deleted successfully.
        """
        person_id = self.person.id  # Store the ID before deletion
        self.person.delete()
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(id=person_id)  # Ensure the object is deleted


class PersonViewSetTests(APITestCase):
    """
    Test cases for the PersonViewSet, covering CRUD operations and permissions.
    """
    def setUp(self):
        """
        Set up test data with different user roles.
        """
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
            last_name="Niiv",
            email="john@example.com",
            phone="1234567890",
            date_of_birth=date(1992, 5, 15),
            role=Role.GUEST
        )

        self.person2 = Person.objects.create(
            username="jane_doe",
            first_name="Jane",
            last_name="Niiv",
            email="jane@example.com",
            phone="0987654321",
            date_of_birth=date(1985, 7, 20),
            role=Role.GUEST
        )

    def test_admin_can_list_persons(self):
        """
        Admin should be able to view all persons.
        """
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
        """
        Admin should be able to create a new person.
        """
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
        """
        Guest users should not be able to create a person.
        """
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

    def test_person_list_pagination(self):
        """
        Test the pagination of the Person list API.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertTrue(isinstance(response.data["results"], list))

    def test_person_update(self):
        """
        Update person should return correct results.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-detail", args=[self.person1.id])
        data = {
            "username": "updated-user1",
            "email": "updated@user1.com",
            "phone": "9999999999",
            "date_of_birth": "1995-07-10",
            "role": Role.ADMIN,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.person1.refresh_from_db()
        self.assertEqual(self.person1.username, "updated-user1")
        self.assertEqual(self.person1.email, "updated@user1.com")
        self.assertEqual(self.person1.phone, "9999999999")
        self.assertEqual(self.person1.role, Role.ADMIN)

    def test_person_delete(self):
        """
        Delete person should delete the object.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-detail", args=[self.person2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(id=self.person2.id)

    def test_person_search_by_first_name(self):
        """
        Searching persons by first name should return correct results.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-search") + "?first_name=John"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "John")

    def test_person_search_by_age(self):
        """
        Searching persons by age should return correct results.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        age = date.today().year - 1990
        url = reverse("profiles:person-search") + f"?age={age}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "Prince")

    def test_invalid_age_in_search(self):
        """
        Providing an invalid age should return a 400 error.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        url = reverse("profiles:person-search") + "?age=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Age must be an integer")

    def test_vector_search_by_valid_name(self):
        """
        Vector search should return correct results with a valid name.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=Gust"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vector_search_by_missing_name(self):
        """
        Vector search should return 400 error if name is not provided.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Provide at least one name")

    def test_vector_search_no_results(self):
        """
        Vector search should return 200 with a no results message when no matches are found.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=Unknown"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "No similar persons found")

    def test_vector_search_by_similar_name(self):
        """
        Vector search should return similar persons when a matching name is provided.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.guest_token.key}")
        url = reverse("profiles:person-vector-search") + "?name=Nii"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)


class LoginViewTests(APITestCase):
    """
    Test cases for the login view, verifying authentication and token generation.
    """
    def setUp(self):
        """
        Set up a test user for authentication tests.
        """
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
        """
        A user with correct credentials should receive a token.
        """
        response = self.client.post(
            self.url, {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_unsuccessful(self):
        """
        A user with incorrect credentials should get a 400 error.
        """
        response = self.client.post(
            self.url, {"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid credentials")
