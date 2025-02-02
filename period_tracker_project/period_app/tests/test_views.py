"""
This file contains the views for the application period_app.
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from period_app.models import CustomUser, UserProfile, HealthAndCycleFormModel


@pytest.mark.django_db
class TestRegisterView:
    """
    Tests for user registration view.
    """
    def test_get_register_view(self):
        """
        Test if the register view displays correctly.
        """
        client = Client()
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'register.html' in [t.name for t in response.templates]

    def test_successful_registration(self):
        """
        Test successful user registration.
        """
        client = Client()
        data = {
            'username': 'testuser',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
            'email': 'test@example.com'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 302
        assert CustomUser.objects.filter(username='testuser').exists()
        assert UserProfile.objects.filter(user__username='testuser').exists()

    def test_invalid_registration(self):
        """
        Test registration with invalid data.
        """
        client = Client()
        data = {
            'username': 'testuser',
            'password1': 'pass',
            'password2': 'pass',
            'email': 'invalid_email'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert len(response.context['form'].errors) > 0


@pytest.mark.django_db
class TestLoginView:
    """
    Tests for user login view.
    """
    @pytest.fixture
    def user(self):
        return CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_successful_login(self, user):
        """
        Test successful user login.
        """
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        assert response.status_code == 302
        assert response.url == reverse('home')

    def test_invalid_credentials(self, user):
        """
        Test login with invalid credentials.
        """
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.django_db
class TestHomeView:
    """
    Tests for home view.
    """
    @pytest.fixture
    def authenticated_client(self):
        """
        Test home view for authenticated user.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        UserProfile.objects.create(user=user)
        client = Client()
        client.login(username='testuser', password='testpassword123')
        return client

    def test_home_view_with_cycle_data(self, authenticated_client):
        """
        Test home view when user has cycle data.
        """
        user = CustomUser.objects.get(username='testuser')
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            menstruation_phase_start=timezone.now().date(),
            cycle_length=28,
            period_length=5
        )
        
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 200
        assert 'cycle_info' in response.context
        assert response.context['cycle_info'] is not None

    def test_home_view_without_cycle_data(self, authenticated_client):
        """
        Test home view when user has no cycle data.
        """
        response = authenticated_client.get(reverse('home'))
        assert response.status_code == 200
        assert 'error' in response.context


@pytest.mark.django_db
class TestCalendarView:
    """
    Tests for calendar view.
    """
    @pytest.fixture
    def authenticated_client(self):
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        UserProfile.objects.create(user=user)
        client = Client()
        client.login(username='testuser', password='testpassword123')
        return client, user

    def test_get_events_ajax(self, authenticated_client):
        """
        Test AJAX request for calendar events.
        """
        client, user = authenticated_client
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=timezone.now().date(),
            event="Test Event",
            menstruation_phase_start=timezone.now().date(),
            cycle_length=28
        )
        
        response = client.get(
            reverse('calendar'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_delete_event(self, authenticated_client):
        """
        Test event deletion.
        """
        client, user = authenticated_client
        event = HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=timezone.now().date(),
            event="Test Event"
        )
        
        response = client.post(reverse('calendar'), {
            'action': 'delete',
            'event_id': event.id
        })
        assert response.status_code == 200
        assert not HealthAndCycleFormModel.objects.filter(id=event.id).exists()


@pytest.mark.django_db
class TestCycleHealthFormView:
    """
    Tests for health and cycle form view.
    """
    @pytest.fixture
    def authenticated_client(self):
        """
        Test health and cycle form view for authenticated user.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        UserProfile.objects.create(user=user)
        client = Client()
        client.login(username='testuser', password='testpassword123')
        return client, user

    def test_form_submission(self, authenticated_client):
        """
        Test successful form submission.
        """
        client, user = authenticated_client
        form_data = {
            'date': timezone.now().date(),
            'event': 'Test Event',
            'daily_symptoms': ['Ból głowy', 'Zmęczenie'],
            'daily_mood': ['Szczęście'],
            'average_pain_level': '3',
            'cycle_length': 28,
            'period_length': 6,
            'menstruation_phase_start': timezone.now().date(),
            'menstruation_phase_end': (timezone.now() + timedelta(days=6)).date(),
        }

        response = client.post(reverse('form'), form_data)
        assert response.status_code == 302
        assert response.url == reverse('calendar')
        assert HealthAndCycleFormModel.objects.filter(
            user_profile=user.userprofile,
            event='Test Event'
        ).exists()


@pytest.mark.django_db
class TestStatisticsView:
    """
    Tests for statistics view.
    """
    @pytest.fixture
    def authenticated_client(self):
        """
        Test statistics view for authenticated user.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        UserProfile.objects.create(user=user)
        client = Client()
        client.login(username='testuser', password='testpassword123')
        return client, user

    def test_statistics_with_data(self, authenticated_client):
        """
        Test statistics view with existing data.
        """
        client, user = authenticated_client
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=timezone.now().date(),
            daily_symptoms=['Ból głowy'],
            daily_mood=['Szczęście'],
            average_pain_level=3,
            recorded_at=timezone.now()
        )

        response = client.get(reverse('statistics'))
        assert response.status_code == 200
        assert 'chart_data' in response.context
        assert 'symptoms' in response.context['chart_data']
        assert 'moods' in response.context['chart_data']
        assert 'pain_levels' in response.context['chart_data']

    def test_pdf_export(self, authenticated_client):
        """
        Test PDF export functionality.
        """
        client, user = authenticated_client
        HealthAndCycleFormModel.objects.create(
            user_profile=user.userprofile,
            date=timezone.now().date(),
            daily_symptoms=['Ból głowy'],
            daily_mood=['Szczęście'],
            average_pain_level=3,
            recorded_at=timezone.now()
        )

        response = client.get(reverse('export_statistics_pdf'))
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
