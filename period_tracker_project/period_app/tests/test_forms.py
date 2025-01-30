import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from period_app.forms import CustomUserCreationForm, UserLoginForm, HealthAndCycleForm
from period_app.models import UserProfile
from datetime import date, timedelta


@pytest.mark.django_db
class TestCustomUserCreationForm(TestCase):
    def test_valid_user_creation_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        assert form.is_valid()

    def test_invalid_email(self):
        form_data = {
            'username': 'testuser2',
            'email': 'invalid-email',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_passwords_dont_match(self):
        form_data = {
            'username': 'testuser3',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'differentpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid()

    def test_save_user(self):
        form_data = {
            'username': 'testuser4',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        user = form.save()
        assert user.username == 'testuser4'
        assert user.email == 'test@example.com'
        assert user.check_password('testpassword123')


@pytest.mark.django_db
class TestUserLoginForm(TestCase):
    def test_valid_login_form(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        form = UserLoginForm(data=form_data)
        assert form.is_valid()

    def test_empty_fields(self):
        form_data = {}
        form = UserLoginForm(data=form_data)
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'password' in form.errors


@pytest.mark.django_db
class TestHealthAndCycleForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.User = get_user_model()

    def setUp(self):
        super().setUp()
        self.user = self.User.objects.create(
            username=f'testuser_{self._testMethodName}',
            email='test@example.com',
            password='testpassword123'
        )
        self.user_profile = UserProfile.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()
        super().tearDown()

    def test_valid_health_cycle_form(self):
        today = date.today()
        form_data = {
            'first_day_of_cycle': today,
            'cycle_length': 28,
            'period_length': 5,
            'last_period_start': today - timedelta(days=28),
            'average_pain_level': 3,
            'menstruation_phase_start': today,
            'menstruation_phase_end': today + timedelta(days=5),
            'allergies': 'None',
            'medications': 'None',
            'health_condition': 'Healthy',
            'daily_symptoms': ['Ból brzucha', 'Zmęczenie'],
            'daily_mood': ['Szczęście', 'Radość'],
            'date': today,
            'event': 'Test event'
        }
        form = HealthAndCycleForm(data=form_data)
        assert form.is_valid(), form.errors

    def test_invalid_dates(self):
        today = date.today()
        form_data = {
            'first_day_of_cycle': today,
            'menstruation_phase_start': today,
            'menstruation_phase_end': today - timedelta(days=1),
            'date': today,
            'event': 'Test event'
        }
        form = HealthAndCycleForm(data=form_data)
        assert form.is_valid(), form.errors

    def test_invalid_cycle_length(self):
        form_data = {
            'cycle_length': 0,
            'date': date.today(),
            'event': 'Test event',
            'first_day_of_cycle': date.today()
        }
        form = HealthAndCycleForm(data=form_data)
        assert not form.is_valid()
        assert 'cycle_length' in form.errors

    def test_required_fields(self):
        form_data = {}
        form = HealthAndCycleForm(data=form_data)
        assert not form.is_valid()
        assert 'first_day_of_cycle' in form.errors
        assert 'date' in form.errors
        assert 'event' in form.errors

    def test_valid_pain_level(self):
        form_data = {
            'average_pain_level': 5,
            'date': date.today(),
            'event': 'Test event',
            'first_day_of_cycle': date.today()
        }
        form = HealthAndCycleForm(data=form_data)
        assert form.is_valid(), form.errors

    def test_invalid_pain_level(self):
        form_data = {
            'average_pain_level': 11,
            'date': date.today(),
            'event': 'Test event',
            'first_day_of_cycle': date.today()
        }
        form = HealthAndCycleForm(data=form_data)
        assert not form.is_valid()

    def test_clean_method(self):
        today = date.today()
        form_data = {
            'first_day_of_cycle': today,
            'daily_symptoms': ['Ból brzucha', 'Zmęczenie'],
            'daily_mood': ['Szczęście', 'Radość'],
            'date': today,
            'event': 'Test event'
        }
        form = HealthAndCycleForm(data=form_data)
        assert form.is_valid(), form.errors
        cleaned_data = form.clean()
        assert isinstance(cleaned_data['daily_symptoms'], list)
        assert isinstance(cleaned_data['daily_mood'], list)