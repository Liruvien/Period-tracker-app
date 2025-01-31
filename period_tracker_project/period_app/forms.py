"""
This module contains forms for user authentication and health cycle tracking in the period_app.
"""

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import HealthAndCycleFormModel


class CustomUserCreationForm(UserCreationForm):
    """
    User creation form that includes an email field.
    """
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Enter email."
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    User login form with username and password fields.
    """
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )


class HealthAndCycleForm(forms.ModelForm):
    """
    Form for tracking health and menstrual cycle details.
    """
    PAIN_LEVEL_CHOICES = [(i, str(i)) for i in range(1, 11)]

    class Meta:
        model = HealthAndCycleFormModel
        fields = [
            'first_day_of_cycle', 'cycle_length', 'period_length',
            'last_period_start', 'average_pain_level',
            'menstruation_phase_start', 'menstruation_phase_end',
            'allergies', 'medications', 'health_condition',
            'daily_symptoms', 'daily_mood', 'date', 'event'
        ]
        widgets = {
            'user_profile': forms.HiddenInput(),
        }

    date = forms.DateField(
        label="Data wydarzenia",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    event = forms.CharField(
        label="Tytuł wydarzenia",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Wpisz nazwę wydarzenia'})
    )

    first_day_of_cycle = forms.DateField(
        label="Pierwszy dzien cyklu",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    last_period_start = forms.DateField(
        label="Data rozpoczęcia ostatniej miesiączki",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    menstruation_phase_start = forms.DateField(
        label="Początek miesiączki",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    menstruation_phase_end = forms.DateField(
        label="Koniec miesiączki",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    period_length = forms.IntegerField(
        label="Długość miesiączki (dni)",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź długość miesiączki'})
    )

    cycle_length = forms.IntegerField(
        label="Długość cyklu (dni)",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź długość cyklu'})
    )

    average_pain_level = forms.ChoiceField(
        label="Średni poziom bólu (1-10)",
        required=False,
        choices=PAIN_LEVEL_CHOICES,
    )

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

    daily_mood = forms.MultipleChoiceField(
        label="Nastrój",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=MOOD_CHOICES,
    )

    daily_symptoms = forms.MultipleChoiceField(
        label="Objawy",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=SYMPTOM_CHOICES,
    )

    allergies = forms.CharField(
        label="Alergie",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': "Wpisz alergie", "rows": 3})
    )

    medications = forms.CharField(
        label="Leki",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': "Wpisz przyjmowane leki", "rows": 3})
    )

    health_condition = forms.CharField(
        label="Stan zdrowia",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': "Opisz stan zdrowia", "rows": 3})
    )

    def __init__(self, *args, **kwargs):
        initial_date = kwargs.get('initial', {}).get('date', timezone.now().date())
        if "initial" not in kwargs:
            kwargs["initial"] = {}
        kwargs["initial"]["date"] = initial_date
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        daily_symptoms = cleaned_data.get("daily_symptoms", [])
        daily_mood = cleaned_data.get("daily_mood", [])
        if daily_symptoms:
            cleaned_data["daily_symptoms"] = list(daily_symptoms)
        if daily_mood:
            cleaned_data["daily_mood"] = list(daily_mood)
        return cleaned_data
