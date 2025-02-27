# Django Project - obviously

## Overview
This is a Django-based REST API for managing Person entities. It provides user authentication, role-based access control, CRUD operations, and filtering functionalities. The project uses Django ORM with an in-memory SQLite database and includes customized API error responses.

## Features
- **Authentication**: In-memory user-based token authentication with predefined roles (`admin`, `guest`).
- **Django ORM with SQLite**: Uses Django's ORM with an in-memory SQLite database.
- **CRUD Operations**: Standard RESTful endpoints with pagination (admin only).
- **Filtering**: Search persons by first name, last name (partial match), or age (admin and guest access).
- **Security**: Username and password fields are excluded from responses.
- **Custom API Errors**: Provides structured and meaningful API error messages.

## Bonus Features (Optional)
- **Optimized Docker Image**: Containerized deployment with an optimized Docker setup.
- **Vector Database Similarity Search**: Integrates a vector database for finding similar profiles based on embeddings.

## Installation
### Prerequisites
- Python 3.8+
- Django
- Django REST Framework
- SQLite (built-in with Python)
- Docker (for containerization, optional)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/prashant-niiv/obviously.git
   cd obviously
   ```
2. Create and activate a virtual environment:
   ```sh
   virtualenv -p python3 venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Create superuser:
   ```sh
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```sh
   python manage.py runserver
   ```

## API Endpoints
### Authentication
- `POST /api/profiles/login/` - Obtain authentication token

### Person Management (Admin Only)
- `GET /api/profiles/persons/` - List persons (paginated)
- `POST /api/profiles/persons/` - Create a person
- `GET /api/profiles/persons/{id}/` - Retrieve person details
- `PUT /api/profiles/persons/{id}/` - Update a person
- `DELETE /api/profiles/persons/{id}/` - Delete a person

### Filtering (Admin & Guest)
- `GET /api/profiles/persons/search/?first_name=John&age=30` - Search by name (partial match) and/or age

## Running with Docker (Optional)
1. Build the Docker image:
   ```sh
   docker build -t obviously .
   ```
2. Run the container:
   ```sh
   docker run -p 8000:8000 obviously
   ```

## Vector Search (Optional)
- `GET /api/profiles/persons/vector_search/?name=John` - Uses a vector database to find similar profiles based on embeddings.



