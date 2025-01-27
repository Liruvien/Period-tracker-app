from django import forms
from .models import HealthAndCycleFormModel
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    """
    User creation form.
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
    User login form.
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
        required=True,
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
        widget=forms.NumberInput(attrs={'placeholder': 'Wprowadź średni poziom bólu'}),
        choices=PAIN_LEVEL_CHOICES,
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

    daily_mood = forms.MultipleChoiceField(
        label="Nastrój",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=HealthAndCycleFormModel.MOOD_CHOICES,
    )

    daily_symptoms = forms.MultipleChoiceField(
         label="Objawy",
         required=False,
         widget=forms.CheckboxSelectMultiple,
         choices=HealthAndCycleFormModel.SYMPTOM_CHOICES,
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
    health_condition = forms.CharField(
        label="Stan zdrowia",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Opisz stan zdrowia', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize form with default date.
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        initial_date = kwargs.get('initial', {}).get('date', timezone.now().date())
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        kwargs['initial']['date'] = initial_date
        super().__init__(*args, **kwargs)
