from django.urls import path

from usuarios.views import LoginView, csrf

from .views import health

urlpatterns = [
    path("health", health),
    path("auth/csrf", csrf),
    path("auth/login", LoginView.as_view()),
]
