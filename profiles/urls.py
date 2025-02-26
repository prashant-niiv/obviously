from django.urls import include, path

from rest_framework.routers import DefaultRouter

from profiles.views import LoginView, PersonViewSet

app_name = 'profiles'  # Namespace for URL reversal

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'persons', PersonViewSet, basename='person')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Login endpoint
    path('', include(router.urls)),  # Include all routes from the router
]
