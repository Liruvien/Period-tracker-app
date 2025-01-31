"""
This module contains test cases for views in the period tracking application.
"""

import pytest
from django.test import Client
from django.urls import reverse
from period_app.models import CustomUser, UserProfile


@pytest.mark.django_db
def test_home_view_authenticated():
    """Test if an authenticated user can access the home view."""
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_view_unauthenticated():
    """Test if an unauthenticated user is redirected from the home view."""
    client = Client()
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_register_view():
    """Test if the register view is accessible."""
    client = Client()
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_view():
    """Test if the login view is accessible."""
    client = Client()
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_view():
    """Test if an authenticated user can log out."""
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_calendar_view_authenticated():
    """Test if an authenticated user can access the calendar view."""
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('calendar')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_calendar_view_unauthenticated():
    """Test if an unauthenticated user is redirected from the calendar view."""
    client = Client()
    url = reverse('calendar')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_cycle_health_form_view_authenticated():
    """Test if an authenticated user can access the cycle health form view."""
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    UserProfile.objects.create(user=user)
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('form')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_statistics_view_authenticated():
    """Test if an authenticated user can access the statistics view."""
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    UserProfile.objects.create(user=user)
    client = Client()
    client.login(username='testuser', password='testpassword')
    url = reverse('statistics')
    response = client.get(url)
    assert response.status_code == 200
