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
        ('1', 'Ból brzucha'),
        ('2', 'Ból pleców'),
        ('3', 'Ból nóg'),
        ('4', 'Ból w klatce piersiowej'),
        ('5', 'Ból głowy'),
        ('6', 'Ból ramion'),
        ('7', 'Kłucie w pochwie'),
        ('8', 'Podwyższona temperatura ciała'),
        ('9', 'Obniżona temperatura ciała'),
        ('10', 'Biegunka'),
        ('11', 'Zaparcia'),
        ('12', 'Zgaga'),
        ('13', 'Obrzęk'),
        ('14', 'Trądzik'),
        ('15', 'Dusznosci'),
        ('16', 'Wahania nastroju'),
        ('17', 'Wzdęcia'),
        ('18', 'Krwawienie zastepcze'),
        ('19', 'Zmęczenie'),
    ]
    MOOD_CHOICES = [
        ('1', 'Szczęście'),
        ('2', 'Entuzjazm'),
        ('3', 'Ekscytacja'),
        ('4', 'Smutek'),
        ('5', 'Rozpacz'),
        ('6', 'Lęk'),
        ('7', 'Irytacja'),
        ('8', 'Gniew'),
        ('9', 'Radość'),
        ('10', 'Placz'),
        ('11', 'Strach'),
        ('12', 'Złość'),
        ('13', 'Wstręt'),
        ('14', 'Rozpacz'),
        ('15', 'Panika'),
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
    daily_symptoms = models.CharField(max_length=255, choices=SYMPTOM_CHOICES, blank=True)
    daily_mood = models.CharField(max_length=255, choices=MOOD_CHOICES, blank=True)
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
