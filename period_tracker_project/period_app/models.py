from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Abstract user model.
    """
    weight = models.PositiveIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    User profile model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile', null=False, blank=False)

    def __str__(self):
        return f"{self.user.username}'s profile"


class HealthAndCycleFormModel(models.Model):
    """
    Model for tracking menstrual and health information.
    """
    PAIN_LEVEL_CHOICES = [(i, str(i)) for i in range(1, 11)]
    SYMPTOM_CHOICES = [
        ('Ból brzucha', 'Ból brzucha'),
        ('Ból pleców', 'Ból pleców'),
        ('Ból nóg', 'Ból nóg'),
        ('Ból w klatce piersiowej', 'Ból w klatce piersiowej'),
        ('Ból głowy', 'Ból głowy'),
        ('Ból ramion', 'Ból ramion'),
        ('Kłucie w pochwie', 'Kłucie w pochwie'),
        ('Podwyższona temperatura ciała', 'Podwyższona temperatura ciała'),
        ('Obniżona temperatura ciała', 'Obniżona temperatura ciała'),
        ('Biegunka', 'Biegunka'),
        ('Zaparcia', 'Zaparcia'),
        ('Zgaga', 'Zgaga'),
        ('Obrzęk', 'Obrzęk'),
        ('Trądzik', 'Trądzik'),
        ('Dusznosci', 'Dusznosci'),
        ('Wahania nastroju', 'Wahania nastroju'),
        ('Wzdęcia', 'Wzdęcia'),
        ('Krwawienie zastepcze', 'Krwawienie zastepcze'),
        ('Zmęczenie', 'Zmęczenie'),
    ]
    MOOD_CHOICES = [
        ('Szczęście', 'Szczęście'),
        ('Entuzjazm', 'Entuzjazm'),
        ('Ekscytacja', 'Ekscytacja'),
        ('Smutek', 'Smutek'),
        ('Rozpacz', 'Rozpacz'),
        ('Lęk', 'Lęk'),
        ('Irytacja', 'Irytacja'),
        ('Gniew', 'Gniew'),
        ('Radość', 'Radość'),
        ('Placz', 'Placz'),
        ('Strach', 'Strach'),
        ('Złość', 'Złość'),
        ('Wstręt', 'Wstręt'),
        ('Rozpacz', 'Rozpacz'),
        ('Panika', 'Panika'),
    ]
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False, blank=False)
    first_day_of_cycle = models.DateField(null=True, blank=True)
    cycle_length = models.PositiveIntegerField(null=True, blank=True)
    period_length = models.PositiveIntegerField(null=True, blank=True)
    last_period_start = models.DateField(null=True, blank=True)
    average_pain_level = models.PositiveIntegerField(null=True, blank=True, choices=PAIN_LEVEL_CHOICES)
    menstruation_phase_start = models.DateField(null=True, blank=True)
    menstruation_phase_end = models.DateField(null=True, blank=True)
    follicular_phase_start = models.DateField(null=True, blank=True)
    follicular_phase_end = models.DateField(null=True, blank=True)
    ovulation_phase_start = models.DateField(null=True, blank=True)
    ovulation_phase_end = models.DateField(null=True, blank=True)
    luteal_phase_start = models.DateField(null=True, blank=True)
    luteal_phase_end = models.DateField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    health_condition = models.TextField(null=True, blank=True)
    pregnancy_start = models.DateField(null=True, blank=True)
    pregnancy_end = models.DateField(null=True, blank=True)
    current_cycle_day = models.PositiveIntegerField(null=True, blank=True)
    menstruation_days = models.JSONField(default=list)
    date = models.DateField(null=True, blank=True)
    event = models.TextField(null=True, blank=True)
    daily_symptoms = models.JSONField(default=list)
    daily_mood = models.JSONField(default=list)
    recorded_at = models.DateTimeField(null=True, blank=True, verbose_name="Recorded At")

    def __str__(self):
        return f"{self.user_profile.user.username}'s form - {self.recorded_at.date()}"


class StatisticsCycleInfo(models.Model):
    """
    Model for tracking menstrual cycle statistics and health information.
    """
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=False, blank=False, related_name="cycle_info")
    first_day_of_cycle = models.DateField(null=True, blank=True)
    cycle_length = models.PositiveIntegerField(null=True, blank=True)
    period_length = models.PositiveIntegerField(null=True, blank=True)
    last_period_start = models.DateField(null=True, blank=True)
    average_pain_level = models.PositiveIntegerField(null=True, blank=True, choices=HealthAndCycleFormModel.PAIN_LEVEL_CHOICES)
    menstruation_phase_start = models.DateField(null=True, blank=True)
    menstruation_phase_end = models.DateField(null=True, blank=True)
    menstruation_days = models.JSONField(default=list)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    health_condition = models.TextField(null=True, blank=True)
    daily_symptoms = models.CharField(max_length=255, choices=HealthAndCycleFormModel.SYMPTOM_CHOICES, blank=True)
    daily_mood = models.CharField(max_length=255, choices=HealthAndCycleFormModel.MOOD_CHOICES, blank=True)
    current_cycle_day = models.PositiveIntegerField(null=True, blank=True)
    pregnancy_start = models.DateField(null=True, blank=True)
    pregnancy_end = models.DateField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    event = models.TextField(null=True, blank=True)
    recorded_at = models.DateTimeField(null=True, blank=True, verbose_name="Recorded At")
    def __str__(self):
        return f"{self.user_profile.user.username}'s cycle statistics - {self.recorded_at.date()}"
