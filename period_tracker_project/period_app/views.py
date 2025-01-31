"""
This file contains the views for the application period_app.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from io import BytesIO
from collections import defaultdict

from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib import messages

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

from .forms import UserLoginForm, HealthAndCycleForm, CustomUserCreationForm
from .models import HealthAndCycleFormModel, UserProfile
from .utils import calculate_cycle_phases



class RegisterView(CreateView):
    """
    View for user registration. Handles the form for creating a new user.
    """
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Handles the form validation. If valid, creates a UserProfile object for the new user.
        """
        response = super().form_valid(form)
        UserProfile.objects.create(user=self.object)
        return response


class LoginView(FormView):
    """
    View for user login. Handles the login form and authentication.
    """
    form_class = UserLoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        Authenticates the user using the provided credentials and logs them in.
        """
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            return super().form_valid(form)
        form.add_error(None, 'Invalid credentials')
        return self.form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    View for user logout. Logs out the user and redirects to the login page.
    """
    next_page = reverse_lazy('login')

class Home(LoginRequiredMixin, View):
    """
    Home view for logged-in users. Displays current cycle information.
    """
    redirect_field_name = 'next'
    template_name = 'home.html'

    def get(self, request):
        """Handle GET request and display cycle information."""
        try:
            user_profile = request.user.userprofile
            cycle_info = self.get_current_cycle_info(user_profile)
        except AttributeError:
            return render(request, self.template_name, {'error': 'User profile not found'})

        if not cycle_info:
            return render(request, self.template_name, {'error': 'Brak danych o cyklu'})

        current_phase = self.get_phase_for_day(cycle_info['cycle_day'], cycle_info['cycle_length'])
        hormone_levels = self.get_hormone_levels(current_phase)
        phase_info = self.get_phase_description(current_phase)
        next_period = self.predict_next_period(cycle_info)

        context = {
            'cycle_info': cycle_info,
            'current_phase': current_phase,
            'hormone_levels': hormone_levels,
            'phase_info': phase_info,
            'next_period': next_period
        }

        return render(request, self.template_name, context)

    def get_current_cycle_info(self, user_profile) -> Dict[str, Any] | None:
        """
        Retrieve the current cycle information.
        """
        latest_period_entry = (HealthAndCycleFormModel.objects
                             .filter(
                                user_profile=user_profile,
                                menstruation_phase_start__isnull=False
                             )
                             .order_by('-menstruation_phase_start')
                             .first())

        if not latest_period_entry:
            return None

        today = datetime.now().date()
        start_date = latest_period_entry.menstruation_phase_start
        if latest_period_entry.cycle_length:
            cycle_length = latest_period_entry.cycle_length
        else:
            cycle_length = 28
        days_since_start = (today - start_date).days
        if days_since_start >= 0:
            current_cycle_day = (days_since_start % cycle_length) + 1
        else:
            return None
        first_day = None
        if latest_period_entry.first_day_of_cycle:
            first_day = latest_period_entry.first_day_of_cycle
        else:
            first_day = start_date

        return {
            'cycle_day': current_cycle_day,
            'cycle_length': cycle_length,
            'first_day': first_day,
            'period_length': latest_period_entry.period_length or 6,
        }

    def get_phase_for_day(self, cycle_day: int, cycle_length: int) -> str:
        """
        Determine cycle phase for given day.
        """
        phase_lengths = {
            'menstruation': 6,
            'follicular': 9,
            'ovulation': 1,
            'luteal': cycle_length - 19
        }

        if cycle_day <= phase_lengths['menstruation']:
            return 'menstruation'
        if cycle_day <= phase_lengths['menstruation'] + phase_lengths['follicular']:
            return 'follicular'
        if cycle_day <= phase_lengths['menstruation'] + phase_lengths['follicular'] + phase_lengths['ovulation']:
            return 'ovulation'
        return 'luteal'

    def get_hormone_levels(self, phase: str) -> Dict[str, float]:
        """
        Return approximate hormone levels for given phase.
        """
        hormone_levels = {
            'menstruation': {
                'estrogen': 20.0,
                'progesterone': 10.0,
                'fsh': 40.0,
                'lh': 20.0
            },
            'follicular': {
                'estrogen': 60.0,
                'progesterone': 20.0,
                'fsh': 70.0,
                'lh': 30.0
            },
            'ovulation': {
                'estrogen': 90.0,
                'progesterone': 30.0,
                'fsh': 90.0,
                'lh': 100.0
            },
            'luteal': {
                'estrogen': 40.0,
                'progesterone': 90.0,
                'fsh': 20.0,
                'lh': 20.0
            }
        }
        return hormone_levels.get(phase, {})

    def get_phase_description(self, phase: str) -> Dict[str, str]:
        """
        Returns a description of the given menstrual cycle phase, including symptoms,
        recommendations, exercise advice, and nutritional guidelines.
        """
        descriptions = {
            'menstruation': {
                'description': 'Rozpoczyna się nowy cykl. Poziom hormonów jest niski.',
                'symptoms': 'Możliwe bóle brzucha, zmęczenie, wahania nastroju.',
                'recommendations': 'Zadbaj o odpoczynek, unikaj nadmiernego wysiłku, zwróć uwagę na higienę.',
                'exercise': 'Lekkie ćwiczenia, spacery, stretching.',
                'nutrition': 'Zwiększ spożycie żelaza i witaminy B12, pij dużo wody.'
            },
            'follicular': {
                'description': 'Poziom estrogenów wzrasta, przygotowując organizm do owulacji.',
                'symptoms': 'Wzrost energii, poprawa nastroju, większa kreatywność.',
                'recommendations': 'To dobry czas na nowe projekty i aktywność fizyczną.',
                'exercise': 'Możesz zwiększyć intensywność treningu.',
                'nutrition': 'Zrównoważona dieta bogata w proteiny i warzywa.'
            },
            'ovulation': {
                'description': 'Szczyt płodności. Wysoki poziom estrogenów i LH.',
                'symptoms': 'Możliwy ból owulacyjny, zwiększone libido.',
                'recommendations': 'Obserwuj objawy owulacji jeśli planujesz ciążę.',
                'exercise': 'Możesz kontynuować regularne treningi.',
                'nutrition': 'Zwiększ spożycie antyoksydantów i kwasów omega-3.'
            },
            'luteal': {
                'description': 'Wzrost poziomu progesteronu. Organizm przygotowuje się do następnego cyklu.',
                'symptoms': 'Możliwe PMS, wahania nastroju, zatrzymanie wody.',
                'recommendations': 'Zadbaj o regularny sen i techniki relaksacyjne.',
                'exercise': 'Umiarkowana aktywność fizyczna, joga.',
                'nutrition': 'Ogranicz sól i cukry proste, zwiększ spożycie magnezu.'
            }
        }
        return descriptions.get(phase, {})

    def predict_next_period(self, cycle_info: Dict) -> datetime.date:
        """
        Predicts the next expected period start date based on the provided cycle information.
        """
        if not cycle_info or not cycle_info.get('first_day'):
            return None

        first_day = cycle_info['first_day']
        cycle_length = cycle_info['cycle_length']
        days_since_start = (datetime.now().date() - first_day).days
        completed_cycles = days_since_start // cycle_length
        next_period = first_day + timedelta(days=(completed_cycles + 1) * cycle_length)

        return next_period

class CalendarView(LoginRequiredMixin, TemplateView):
    """
    Calendar view for user health and cycle events. Allows viewing and managing events.
    """
    redirect_field_name = 'next'
    template_name = 'calendar.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for rendering the calendar page or responding with AJAX data.
        """
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.get_events(request)
        return render(request, self.template_name)

    def post(self, request):
        """
        Handles POST requests for deleting calendar events and redirect to form .
        """
        action = request.POST.get('action')
        try:
            if action == 'delete':
                return self.delete_event(request)
            return HttpResponseBadRequest("Incorrect action")
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except ValidationError as e:
            return JsonResponse({"error": f"Validation error: {e}"}, status=400)

    @staticmethod
    def get_events(request):
        """
        Retrieves and processes menstrual cycle events.
        """
        events = HealthAndCycleFormModel.objects.filter(user_profile=request.user.userprofile)
        events_data = []

        for event in events:
            phases = calculate_cycle_phases(event.menstruation_phase_start, event.menstruation_phase_end,
                                            event.cycle_length)
            event_date = datetime.combine(event.date, datetime.min.time())
            event_color = None
            menstruation_start = datetime.combine(event.menstruation_phase_start,
                                                  datetime.min.time()) if event.menstruation_phase_start else None
            menstruation_end = datetime.combine(event.menstruation_phase_end,
                                                datetime.min.time()) if event.menstruation_phase_end else None

            for phase_set in phases:
                for phase_name, phase_info in phase_set.items():
                    if phase_info['start'] <= event_date.date() <= phase_info['end']:
                        event_color = phase_info['color']
                        break

            events_data.append({
                "id": event.id,
                "title": event.event,
                "start": event.date.strftime('%Y-%m-%d'),
                "color": event_color,
                "first_day_of_cycle": event.first_day_of_cycle.strftime(
                    '%Y-%m-%d') if event.first_day_of_cycle else None,
                "cycle_length": event.cycle_length,
                "period_length": event.period_length,
                "last_period_start": event.last_period_start.strftime('%Y-%m-%d') if event.last_period_start else None,
                "menstruation_phase_start": event.menstruation_phase_start.strftime(
                    '%Y-%m-%d') if event.menstruation_phase_start else None,
                "menstruation_phase_end": event.menstruation_phase_end.strftime(
                    '%Y-%m-%d') if event.menstruation_phase_end else None,
                "average_pain_level": event.average_pain_level,
                "daily_mood": event.daily_mood,
                "daily_symptoms": event.daily_symptoms,
                "allergies": event.allergies,
                "medications": event.medications,
                "health_condition": event.health_condition,
            })

        return JsonResponse(events_data, safe=False)


    @staticmethod
    def delete_event(request):
        """
        Deletes an existing event.
        """
        event_id = request.POST.get('event_id')
        try:
            event = HealthAndCycleFormModel.objects.get(
                id=event_id,
                user_profile=request.user.userprofile
            )
            event.delete()
            return JsonResponse({"message": "Event deleted"})
        except HealthAndCycleFormModel.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)


class CycleHealthFormView(LoginRequiredMixin, View):
    """
    View for displaying and submitting the health and cycle form.
    """
    template_name = 'form.html'
    redirect_field_name = 'next'

    def get(self, request):
        """
        Handles GET requests to render the health and cycle form.
        """
        selected_date = timezone.now().date()
        form = HealthAndCycleForm(initial={'date': selected_date})
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Handles POST requests to save the form data.
        """
        form = HealthAndCycleForm(request.POST)
        if form.is_valid():
            try:
                form.instance.user_profile = request.user.userprofile
                form.instance.recorded_at = timezone.now()
                form.save()
                messages.success(request, "Form saved.")
                return redirect('calendar')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        return render(request, self.template_name, {'form': form})


class StatisticsView(LoginRequiredMixin, TemplateView):
    """
    View for displaying user statistics related to menstrual cycle tracking.
    """
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        """
        Retrieves and processes menstrual cycle-related data for the authenticated user.
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        today = now().date()
        one_year_ago = today - timedelta(days=365)

        forms = HealthAndCycleFormModel.objects.filter(
            user_profile=user_profile,
            recorded_at__date__gte=one_year_ago
        ).order_by('recorded_at')

        symptom_data = defaultdict(list)
        for form in forms:
            date_str = form.recorded_at.strftime('%Y-%m-%d')
            for symptom in form.daily_symptoms:
                symptom_data[symptom].append(date_str)

        mood_data = defaultdict(list)
        for form in forms:
            date_str = form.recorded_at.strftime('%Y-%m-%d')
            for mood in form.daily_mood:
                mood_data[mood].append(date_str)

        pain_data = defaultdict(list)
        for form in forms:
            date_str = form.recorded_at.strftime('%Y-%m-%d')
            if form.average_pain_level:
                pain_level = int(form.average_pain_level)
                pain_data[pain_level].append(date_str)

        context['chart_data'] = {
            'symptoms': {
                'labels': list(symptom_data.keys()),
                'data': [len(dates) for dates in symptom_data.values()],
                'dates': list(symptom_data.values())
            },
            'moods': {
                'labels': list(mood_data.keys()),
                'data': [len(dates) for dates in mood_data.values()],
                'dates': list(mood_data.values())
            },
            'pain_levels': {
                'labels': list(map(str, pain_data.keys())),
                'data': [len(dates) for dates in pain_data.values()],
                'dates': list(pain_data.values())
            }
        }
        return context


class ExportStatisticsPDFView(LoginRequiredMixin, View):
    """
    View for exporting user statistics related to menstrual cycle tracking as a PDF.
    """
    def get(self, request):
        """
        Handles GET requests to generate a PDF report of user statistics.
        """
        user_profile = request.user.userprofile
        today = now().date()
        one_year_ago = today - timedelta(days=365)

        forms = HealthAndCycleFormModel.objects.filter(
            user_profile=user_profile,
            recorded_at__date__gte=one_year_ago
        ).order_by('recorded_at')

        symptom_data = defaultdict(list)
        mood_data = defaultdict(list)
        pain_data = defaultdict(list)

        for form in forms:
            date_str = form.recorded_at.strftime('%Y-%m-%d')
            for symptom in form.daily_symptoms:
                symptom_data[symptom].append(date_str)
            for mood in form.daily_mood:
                mood_data[mood].append(date_str)
            if form.average_pain_level:
                pain_level = int(form.average_pain_level)
                pain_data[pain_level].append(date_str)

        return self._generate_pdf(request, symptom_data, mood_data, pain_data)

    def _create_table(self, data, title):
        """
        Creates a formatted table for the PDF report.
        """
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(title, styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))

        table_data = [['Type', 'Number of occurrences', 'Daty']]
        for item, dates in data.items():
            table_data.append([
                Paragraph(str(item), styles['Normal']),
                Paragraph(str(len(dates)), styles['Normal']),
                Paragraph(', '.join(dates), styles['Normal'])
            ])

        table = Table(table_data, colWidths=[2 * inch, 2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _generate_pdf(self, request, symptom_data, mood_data, pain_data):
        """
        Generates a PDF report containing menstrual cycle statistics.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        styles = getSampleStyleSheet()
        elements = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Statistics for user: {request.user.username}", title_style))
        elements.append(Paragraph(f"Data: {now().date().strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Spacer(1, 0.4 * inch))

        elements.extend(self._create_table(symptom_data, "Symptoms"))
        elements.extend(self._create_table(mood_data, "Moods"))
        elements.extend(self._create_table(pain_data, "Average pain day level"))

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="statistics.pdf"'
        response.write(pdf)
        return response


class KnowledgeBaseView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the knowledge base page.
    """
    template_name = 'knowledge_base.html'
    redirect_field_name = 'next'


class HormonalHealthView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the hormonal health page.
    """
    template_name = 'hormonal_health.html'
    redirect_field_name = 'next'


class DietImpactView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the diet impact page.
    """
    template_name = 'diet_impact.html'
    redirect_field_name = 'next'


class SelfCareDuringMenstruationView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the page with self-care recommendations during menstruation.
    """
    template_name = 'self_care_menstruation.html'
    redirect_field_name = 'next'


class HealthDuringPregnancyView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the page with health-care recommendations during pregnancy.
    """
    template_name = 'health_during_pregnancy.html'
    redirect_field_name = 'next'
