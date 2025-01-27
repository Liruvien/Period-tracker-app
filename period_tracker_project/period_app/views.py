from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.contrib import messages
from .forms import UserLoginForm, HealthAndCycleForm, CustomUserCreationForm
from .models import HealthAndCycleFormModel, UserProfile
from .utils import calculate_cycle_phases
from django.utils.timezone import now
from django.db.models import Avg, Count
import calendar
from datetime import timedelta
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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

        if user is not None:
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
    Home view for logged-in users. Displays the home page.
    """
    redirect_field_name = 'next'
    template_name = 'home.html'

    def get(self, request):
        return render(request, self.template_name)


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

    def post(self, request, *args, **kwargs):
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
        events = HealthAndCycleFormModel.objects.filter(user_profile=request.user.userprofile)
        events_data = []

        for event in events:
            phases = calculate_cycle_phases(event.menstruation_phase_start, event.menstruation_phase_end,
                                            event.cycle_length)
            event_date = event.date
            event_color = None

            for phase_set in phases:
                for phase_name, phase_info in phase_set.items():
                    if phase_info['start'] <= event_date <= phase_info['end']:
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
        :return: JSON response indicating the result of the operation.
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

    def post(self, request, *args, **kwargs):
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
        else:
            messages.error(request, "KO in form.")

        return render(request, self.template_name, {'form': form})


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.userprofile

        today = now().date()
        one_year_ago = today - timedelta(days=365)

        monthly_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month')
            .annotate(
                average_pain_level=Avg('average_pain_level'),
                event_count=Count('id')
            )
            .order_by('month')
        )

        symptoms_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month', 'daily_symptoms')
            .annotate(symptom_count=Count('id'))
        )

        moods_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month', 'daily_mood')
            .annotate(mood_count=Count('id'))
        )

        months = [calendar.month_name[i] for i in range(1, 13)]
        pain_levels = [0] * 12
        event_counts = [0] * 12

        monthly_symptoms = [{'symptom': 'None', 'count': 0} for _ in range(12)]
        monthly_moods = [{'mood': 'None', 'count': 0} for _ in range(12)]

        for data in monthly_data:
            month_idx = data['month'] - 1
            pain_levels[month_idx] = round(data['average_pain_level'], 2) if data['average_pain_level'] else 0
            event_counts[month_idx] = data['event_count']

        for data in symptoms_data:
            month_idx = data['month'] - 1
            symptom_count = data['symptom_count']
            if symptom_count > monthly_symptoms[month_idx]['count']:
                symptom_name = dict(HealthAndCycleFormModel.SYMPTOM_CHOICES).get(
                    data['daily_symptoms'], 'Unknown'
                )
                monthly_symptoms[month_idx] = {
                    'symptom': symptom_name,
                    'count': symptom_count
                }

        for data in moods_data:
            month_idx = data['month'] - 1
            mood_count = data['mood_count']
            if mood_count > monthly_moods[month_idx]['count']:
                mood_name = dict(HealthAndCycleFormModel.MOOD_CHOICES).get(
                    data['daily_mood'], 'Unknown'
                )
                monthly_moods[month_idx] = {
                    'mood': mood_name,
                    'count': mood_count
                }

        context['chart_data'] = {
            'months': months,
            'pain_levels': pain_levels,
            'event_counts': event_counts,
            'monthly_symptoms': [item['symptom'] for item in monthly_symptoms],
            'monthly_moods': [item['mood'] for item in monthly_moods],
            'symptom_counts': [item['count'] for item in monthly_symptoms],
            'mood_counts': [item['count'] for item in monthly_moods],
        }
        return context


class ExportStatisticsPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_profile = request.user.userprofile
        today = now().date()
        one_year_ago = today - timedelta(days=365)

        # Get numeric data
        monthly_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month')
            .annotate(
                average_pain_level=Avg('average_pain_level'),
                event_count=Count('id')
            )
            .order_by('month')
        )

        # Get symptoms data
        symptoms_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month', 'daily_symptoms')
            .annotate(symptom_count=Count('id'))
        )

        # Get moods data
        moods_data = (
            HealthAndCycleFormModel.objects.filter(
                user_profile=user_profile,
                recorded_at__date__gte=one_year_ago
            )
            .annotate(month=ExtractMonth('recorded_at'))
            .values('month', 'daily_mood')
            .annotate(mood_count=Count('id'))
        )

        monthly_stats = self._process_monthly_stats(symptoms_data, moods_data)
        return self._generate_pdf(request, monthly_data, monthly_stats)

    def _process_monthly_stats(self, symptoms_data, moods_data):
        monthly_stats = {
            month: {
                'most_common_symptom': {'name': 'None', 'count': 0},
                'most_common_mood': {'name': 'None', 'count': 0}
            }
            for month in range(1, 13)
        }

        # Process symptoms
        for data in symptoms_data:
            month = data['month']
            count = data['symptom_count']
            if count > monthly_stats[month]['most_common_symptom']['count']:
                symptom_name = dict(HealthAndCycleFormModel.SYMPTOM_CHOICES).get(
                    data['daily_symptoms'], 'Unknown'
                )
                monthly_stats[month]['most_common_symptom'] = {
                    'name': symptom_name,
                    'count': count
                }

        # Process moods
        for data in moods_data:
            month = data['month']
            count = data['mood_count']
            if count > monthly_stats[month]['most_common_mood']['count']:
                mood_name = dict(HealthAndCycleFormModel.MOOD_CHOICES).get(
                    data['daily_mood'], 'Unknown'
                )
                monthly_stats[month]['most_common_mood'] = {
                    'name': mood_name,
                    'count': count
                }

        return monthly_stats

    def _generate_pdf(self, request, monthly_data, monthly_stats):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        self._draw_header(p, request)
        y = self._draw_column_headers(p)
        self._draw_data_rows(p, monthly_data, monthly_stats, y)

        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="statistics.pdf"'
        response.write(pdf)
        return response

    def _draw_header(self, p, request):
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 800, "User Statistics Report")
        p.drawString(50, 780, f"User: {request.user.username}")
        p.drawString(50, 760, f"Date: {now().date().strftime('%Y-%m-%d')}")

    def _draw_column_headers(self, p):
        y = 720
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Month")
        p.drawString(150, y, "Pain Level")
        p.drawString(250, y, "Most Common")
        p.drawString(250, y - 15, "Symptom")
        p.drawString(350, y, "Most Common")
        p.drawString(350, y - 15, "Mood")
        p.drawString(450, y, "Event")
        p.drawString(450, y - 15, "Count")
        return y - 40

    def _draw_data_rows(self, p, monthly_data, monthly_stats, y):
        p.setFont("Helvetica", 10)

        for data in monthly_data:
            month = data['month']
            month_name = calendar.month_name[month]
            stats = monthly_stats[month]

            # Draw row data
            p.drawString(50, y, month_name)
            p.drawString(150, y, f"{data['average_pain_level']:.1f}" if data['average_pain_level'] else "N/A")

            symptom_text = f"{stats['most_common_symptom']['name']}"
            symptom_count = f"({stats['most_common_symptom']['count']})"
            p.drawString(250, y, symptom_text)
            p.drawString(250, y - 12, symptom_count)

            mood_text = f"{stats['most_common_mood']['name']}"
            mood_count = f"({stats['most_common_mood']['count']})"
            p.drawString(350, y, mood_text)
            p.drawString(350, y - 12, mood_count)

            p.drawString(450, y, str(data['event_count']))

            y -= 30

            # Handle page overflow
            if y < 50:
                p.showPage()
                y = self._draw_column_headers(p)

class KnowledgeBaseView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the knowledge base page.
    """
    redirect_field_name = 'next'
    template_name = 'knowledge_base.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class HormonalHealthView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the hormonal health page.
    """
    redirect_field_name = 'next'
    html_name = 'hormonal_health.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.html_name)


class DietImpactView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the diet impact page.
    """
    redirect_field_name = 'next'
    template_name = 'diet_impact.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SelfCareDuringMenstruationView(LoginRequiredMixin, TemplateView):
    """
    View for displaying page with self-care recommendations during menstruation .
    """
    redirect_field_name = 'next'
    template_name = 'self_care_menstruation.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class HealthDuringPregnancyView(LoginRequiredMixin, TemplateView):
    """
    View for displaying page with health-care recommendations during pregnancy .
    """
    redirect_field_name = 'next'
    template_name = 'health_during_pregnancy.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


