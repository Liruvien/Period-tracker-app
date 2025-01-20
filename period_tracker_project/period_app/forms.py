from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HealthAndCycleFormModel

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nazwa użytkownika'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Hasło'
    }))

class HealthAndCycleForm(forms.ModelForm):
    class Meta:
        model = HealthAndCycleFormModel
        fields = [
            'first_day_of_cycle', 'cycle_length', 'period_length',
            'last_period_start', 'average_pain_level',
            'menstruation_phase_start', 'menstruation_phase_end',
            'follicular_phase_start', 'follicular_phase_end',
            'ovulation_phase_start', 'ovulation_phase_end',
            'luteal_phase_start', 'luteal_phase_end',
            'allergies', 'medications', 'health_conditions',
            'symptoms', 'mood'
        ]

    cycle_length = forms.IntegerField(
        label="Długość cyklu (dni)",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź długość cyklu'})
    )
    period_length = forms.IntegerField(
        label="Długość miesiączki (dni)",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź długość miesiączki'})
    )
    last_period_start = forms.DateField(
        label="Data rozpoczęcia ostatniej miesiączki",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    average_pain_level = forms.IntegerField(
        label="Średni poziom bólu (1-10)",
        required=False,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź średni poziom bólu'})
    )

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
        ('15', 'Dusznica'),
        ('16', 'Wahania nastroju'),
        ('17', 'Wzdęcia'),
        ('18', 'Krwawe stolce'),
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

    mood = forms.MultipleChoiceField(
        label="Nastrój",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=MOOD_CHOICES,
    )

    symptoms = forms.MultipleChoiceField(
        label="Objawy",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=SYMPTOM_CHOICES,
    )

    allergies = forms.CharField(
        label="Alergie",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Wpisz alergie', 'rows': 3})
    )
    medications = forms.CharField(
        label="Leki",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Wpisz przyjmowane leki', 'rows': 3})
    )
    health_conditions = forms.CharField(
        label="Stan zdrowia",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Opisz stan zdrowia', 'rows': 3})
    )

    def clean(self):
        cleaned_data = super().clean()
        cycle_length = cleaned_data.get('cycle_length')
        period_length = cleaned_data.get('period_length')

        if cycle_length and period_length and period_length > cycle_length:
            self.add_error('period_length', "Długość miesiączki nie może być większa niż długość cyklu.")

        return cleaned_data