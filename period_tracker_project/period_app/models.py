from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class HealthAndCycleFormModel(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    first_day_of_cycle = models.DateField(null=True, blank=True)
    cycle_length = models.PositiveIntegerField(null=True, blank=True)
    period_length = models.PositiveIntegerField(null=True, blank=True)
    menstruation_days = models.JSONField(default=list)
    last_period_start = models.DateField(null=True, blank=True)
    average_pain_level = models.PositiveIntegerField(null=True, blank=True, choices=[(i, str(i)) for i in range(1, 11)])
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
    health_conditions = models.TextField(null=True, blank=True)
    pregnancy_start = models.DateField(null=True, blank=True)
    pregnancy_end = models.DateField(null=True, blank=True)

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
        ('15', 'Dusznosc'),
        ('16', 'Wahania nastroju'),
        ('17', 'Wzdęcia'),
        ('18', 'Krwawienie z odbytnicy'),
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
        ('10', 'Smutek'),
        ('11', 'Strach'),
        ('12', 'Złość'),
        ('13', 'Wstręt'),
        ('14', 'Smutek'),
        ('15', 'Panika'),
    ]

    symptoms = models.CharField(max_length=255, choices=SYMPTOM_CHOICES, blank=True)
    mood = models.CharField(max_length=255, choices=MOOD_CHOICES, blank=True)


class StatisticsCycleInfo(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cycle_info')
    cycle_length = models.PositiveIntegerField(null=True, blank=True)
    period_length = models.PositiveIntegerField(null=True, blank=True)
    average_pain_level = models.PositiveIntegerField(
        null=True, blank=True, choices=[(i, str(i)) for i in range(1, 11)]
    )
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    health_conditions = models.TextField(null=True, blank=True)
    symptoms = models.CharField(max_length=255, choices=HealthAndCycleFormModel.SYMPTOM_CHOICES, blank=True)
    mood = models.CharField(max_length=255, choices=HealthAndCycleFormModel.MOOD_CHOICES, blank=True)

    def __str__(self):
        return f"Statistics cycle info for {self.user_profile.user.username}"