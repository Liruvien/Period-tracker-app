import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from period_app.models import UserProfile, HealthAndCycleFormModel, StatisticsCycleInfo
from datetime import date
from django.db import IntegrityError


# Fixtures
@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        weight=60,
        birth_date=date(1990, 1, 1)
    )


@pytest.fixture
def user_profile(user):
    return UserProfile.objects.create(user=user)


@pytest.fixture
def health_form(user_profile):
    return HealthAndCycleFormModel.objects.create(
        user_profile=user_profile,
        first_day_of_cycle=date(2024, 1, 1),
        cycle_length=28,
        period_length=6,
        last_period_start=date(2024, 1, 1),
        average_pain_level=5,
        menstruation_phase_start=date(2024, 1, 1),
        menstruation_phase_end=date(2024, 1, 5),
        allergies="None",
        medications="None",
        health_condition="Healthy",
        daily_symptoms=["Ból głowy", "Zmęczenie"],
        daily_mood=["Szczęście", "Entuzjazm"],
        date=date(2024, 1, 1),
        event="Test event",
        recorded_at=timezone.now()
    )


@pytest.fixture
def statistics_cycle_info(user_profile):
    return StatisticsCycleInfo.objects.create(
        user_profile=user_profile,
        first_day_of_cycle=date(2024, 1, 1),
        cycle_length=28,
        period_length=6,
        last_period_start=date(2024, 1, 1),
        average_pain_level=5,
        menstruation_phase_start=date(2024, 1, 1),
        menstruation_phase_end=date(2024, 1, 5),
        allergies="None",
        medications="None",
        health_condition="Healthy",
        daily_symptoms="Ból głowy",
        daily_mood="Szczęście",
        date=date(2024, 1, 1),
        event="Test event",
        recorded_at=timezone.now()
    )


# CustomUser Tests
@pytest.mark.django_db
class TestCustomUser:
    def test_create_user(self, user):
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.weight == 60
        assert user.birth_date == date(1990, 1, 1)
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_str(self, user):
        assert str(user) == 'testuser'

    def test_optional_fields(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        assert user.weight is None
        assert user.birth_date is None


# UserProfile Tests
@pytest.mark.django_db
class TestUserProfile:
    def test_create_profile(self, user_profile):
        assert user_profile.user.username == 'testuser'

    def test_profile_str(self, user_profile):
        assert str(user_profile) == "testuser's profile"

    def test_user_profile_cascade_delete(self, user_profile):
        user = user_profile.user
        user.delete()
        with pytest.raises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=user_profile.id)

    def test_unique_user_profile(self, user):
        UserProfile.objects.create(user=user)
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user)


# HealthAndCycleFormModel Tests
@pytest.mark.django_db
class TestHealthAndCycleFormModel:
    def test_create_health_form(self, health_form):
        assert health_form.cycle_length == 28
        assert health_form.period_length == 6
        assert len(health_form.daily_symptoms) == 2
        assert len(health_form.daily_mood) == 2

    def test_health_form_str(self, health_form):
        expected_str = f"{health_form.user_profile.user.username}'s form - {health_form.recorded_at.date()}"
        assert str(health_form) == expected_str

    def test_pain_level_validation(self, health_form):
        health_form.average_pain_level = 11
        with pytest.raises(ValidationError):
            health_form.full_clean()

    def test_json_fields_default(self, user_profile):
        form = HealthAndCycleFormModel.objects.create(
            user_profile=user_profile,
            first_day_of_cycle=date(2024, 1, 1)
        )
        assert form.daily_symptoms == []
        assert form.daily_mood == []
        assert form.menstruation_days == []

    def test_required_fields(self, user_profile):
        with pytest.raises(ValidationError):
            form = HealthAndCycleFormModel(user_profile=None)
            form.full_clean()


# StatisticsCycleInfo Tests
@pytest.mark.django_db
class TestStatisticsCycleInfo:
    def test_create_statistics(self, statistics_cycle_info):
        assert statistics_cycle_info.cycle_length == 28
        assert statistics_cycle_info.period_length == 6
        assert statistics_cycle_info.daily_symptoms == "Ból głowy"
        assert statistics_cycle_info.daily_mood == "Szczęście"

    def test_statistics_str(self, statistics_cycle_info):
        expected_str = f"{statistics_cycle_info.user_profile.user.username}'s cycle statistics - {statistics_cycle_info.recorded_at.date()}"
        assert str(statistics_cycle_info) == expected_str

    def test_one_to_one_relationship(self, user_profile):
        stats1 = StatisticsCycleInfo.objects.create(
            user_profile=user_profile,
            cycle_length=28
        )
        with pytest.raises(IntegrityError):
            StatisticsCycleInfo.objects.create(
                user_profile=user_profile,
                cycle_length=30
            )

    def test_pain_level_choices(self, statistics_cycle_info):
        assert statistics_cycle_info.average_pain_level in range(1, 11)
        statistics_cycle_info.average_pain_level = 11
        with pytest.raises(ValidationError):
            statistics_cycle_info.full_clean()

    def test_required_user_profile(self):
        with pytest.raises(IntegrityError):
            StatisticsCycleInfo.objects.create(user_profile=None)