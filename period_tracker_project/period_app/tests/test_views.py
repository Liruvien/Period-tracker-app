"""
This module contains tests for the views in the period_app application.
"""
from datetime import date, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from period_app.models import UserProfile, HealthAndCycleFormModel
from period_app.forms import HealthAndCycleForm


User = get_user_model()

@pytest.fixture
def client():
    """
    Fixture that provides a test client instance to simulate HTTP requests.
    """
    return Client()


@pytest.fixture
def user():
    """
    Fixture that creates a new user along with a user profile for testing.
    """
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user)
    return user


@pytest.fixture
def authenticated_client(client, user):
    """
    Fixture that logs in a user and provides an authenticated client instance.
    """
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def health_form_data():
    """
    Fixture that provides mock data for the health and cycle form.
    """
    return {
        'date': date.today(),
        'event': 'Test Event',
        'first_day_of_cycle': date.today(),
        'cycle_length': 28,
        'period_length': 6,
        'average_pain_level': 3,
        'daily_symptoms': ['Ból brzucha', 'Zmęczenie'],
        'daily_mood': ['Szczęście', 'Radość'],
        'allergies': 'None',
        'medications': 'None',
        'health_condition': 'Good'
    }


@pytest.mark.django_db
class TestRegisterView:
    """
    Tests for the registration view of the application.
    """
    def test_get_register_page(self, client):
        """
        Test to check if the registration page is accessible.
        """
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'register.html' in [t.name for t in response.templates]

    def test_successful_registration(self, client):
        """
        Test to check the registration process and if a new user is created.
        """
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 302
        assert get_user_model().objects.filter(username='newuser').exists()
        assert UserProfile.objects.filter(user__username='newuser').exists()


@pytest.mark.django_db
class TestLoginView:
    """
    Tests for the login view of the application.
    """
    def test_get_login_page(self, client):
        """
        Test to check if the login page is accessible.
        """
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates]

    def test_successful_login(self, client, user):
        """
        Test to check the login functionality with valid credentials.
        """
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(reverse('login'), data)
        assert response.status_code == 302
        assert response.url == reverse('home')

    def test_failed_login(self, client):
        """
        Test to check the login functionality with invalid credentials.
        """
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = client.post(reverse('login'), data)
        assert response.status_code == 200
        assert 'Invalid credentials' in response.context['form'].errors['__all__']


@pytest.mark.django_db
class TestHomeView:
    """
    Tests for the home view of the application.
    """
    def test_unauthenticated_access(self, client):
        """
        Test to check if unauthenticated users are redirected to the login page.
        """
        response = client.get(reverse('home'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_authenticated_access(self, authenticated_client, user):
        """
        Test to check if authenticated users can access the home page.
        """
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 200
        assert 'home.html' in [t.name for t in response.templates]

    def test_home_with_cycle_data(self, authenticated_client, user):
        """
        Test to check if cycle data appears on the home page for authenticated users.
        """
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            menstruation_phase_start=date.today() - timedelta(days=5),
            cycle_length=28,
            first_day_of_cycle=date.today() - timedelta(days=5),
            period_length=5
        )
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 200
        assert 'cycle_info' in response.context


@pytest.mark.django_db
class TestCalendarView:
    """
    Tests for the calendar view of the application.
    """
    def test_unauthenticated_access(self, client):
        """
        Test to check if unauthenticated users are redirected to the login page.

        """
        response = client.get(reverse('calendar'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_get_calendar_page(self, authenticated_client):
        """
        Test to check if the calendar page is accessible for authenticated users.
        """
        response = authenticated_client.get(reverse('calendar'))
        assert response.status_code == 200
        assert 'calendar.html' in [t.name for t in response.templates]

    def test_get_events_ajax(self, authenticated_client, user):
        """
        Test to check if events are fetched correctly via AJAX for the calendar page.
        """
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=date.today(),
            event='Test Event',
            menstruation_phase_start=date.today(),
            cycle_length=28
        )
        response = authenticated_client.get(
            reverse('calendar'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        assert len(response.json()) > 0


@pytest.mark.django_db
class TestCycleHealthFormView:
    """
    Tests for the cycle health form view.
    """
    def test_unauthenticated_access(self, client):
        """
        Test to check if unauthenticated users are redirected to the login page.
        """
        response = client.get(reverse('form'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_get_form_page(self, authenticated_client):
        """
        Test to check if the health and cycle form page is accessible for authenticated users.
        """
        response = authenticated_client.get(reverse('form'))
        assert response.status_code == 200
        assert 'form.html' in [t.name for t in response.templates]
        assert isinstance(response.context['form'], HealthAndCycleForm)

    def test_submit_form(self, authenticated_client, health_form_data):
        """
        Test to check if the health and cycle form is successfully submitted and stored.
        """
        response = authenticated_client.post(reverse('form'), health_form_data)
        assert response.status_code == 302
        assert response.url == reverse('calendar')
        assert HealthAndCycleFormModel.objects.filter(event='Test Event').exists()


@pytest.mark.django_db
class TestStatisticsView:
    """
    Tests for the statistics view of the application.
    """
    def test_authenticated_access(self, authenticated_client):
        """
        Test to check if authenticated users can access the statistics page.
        """
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 302

    def test_get_statistics_page(self, authenticated_client, user):
        """
        Test to check if the statistics page is accessible for authenticated users.
        """
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=date.today(),
            average_pain_level=5,
            daily_symptoms=['Ból brzucha'],
            daily_mood=['Szczęście'],
            recorded_at=timezone.now()
        )

        response = authenticated_client.get(reverse('statistics'))
        assert response.status_code == 200
        assert 'statistics.html' in [t.name for t in response.templates]
        assert 'chart_data' in response.context

    def test_statistics_data_structure(self, authenticated_client, user):
        """
        Test to ensure the structure of the chart data returned for the statistics page is correct.
        """
        response = authenticated_client.get(reverse('statistics'))
        chart_data = response.context['chart_data']
        assert 'months' in chart_data
        assert 'pain_levels' in chart_data
        assert 'event_counts' in chart_data
        assert 'monthly_symptoms' in chart_data
        assert 'monthly_moods' in chart_data
