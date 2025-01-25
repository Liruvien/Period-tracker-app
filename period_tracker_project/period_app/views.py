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
from .models import HealthAndCycleFormModel, StatisticsCycleInfo, UserProfile


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
        Handles POST requests for editing or deleting calendar events.
        """
        action = request.POST.get('action')
        try:
            if action == 'edit':
                return self.edit_event(request)
            elif action == 'delete':
                return self.delete_event(request)

            return HttpResponseBadRequest("Incorrect action")

        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except ValidationError as e:
            return JsonResponse({"error": f"Validation error: {e}"}, status=400)

    @staticmethod
    def get_events(request):
        """
        Retrieves all events associated with the logged-in user.
        Returns: JSON response indicating the result of the operation.
        """
        events = HealthAndCycleFormModel.objects.filter(user_profile=request.user.userprofile)
        events_data = [
            {
                "id": event.id,
                "title": event.event,
                "start": event.date.strftime('%Y-%m-%d'),
                "first_day_of_cycle": event.first_day_of_cycle,
                "cycle_length": event.cycle_length,
                "period_length": event.period_length,
                "last_period_start": event.last_period_start,
                "menstruation_phase_start": event.menstruation_phase_start,
                "menstruation_phase_end": event.menstruation_phase_end,
                "average_pain_level": event.average_pain_level,
                "daily_mood": event.daily_mood,
                "daily_symptoms": event.daily_symptoms,
                "allergies": event.allergies,
                "medications": event.medications,
                "health_conditions": event.health_conditions,
            }
            for event in events
        ]
        return JsonResponse(events_data, safe=False)

    @staticmethod
    def edit_event(request):
        """
        Edits an existing event.
        :return: JSON response indicating success or error.
        """
        event_id = request.POST.get('event_id')
        event = HealthAndCycleFormModel.objects.get(
            id=event_id,
            user_profile=request.user.userprofile
        )
        form = HealthAndCycleForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Event updated"})
        return JsonResponse({"error": form.errors}, status=400)

    @staticmethod
    def delete_event(request):
        """
        Deletes an existing event.
        :return: JSON response indicating the result of the operation.
        """
        event_id = request.POST.get('event_id')
        event = HealthAndCycleFormModel.objects.get(
            id=event_id,
            user_profile=request.user.userprofile
        )
        event.delete()
        return JsonResponse({"message": "Event deteted"})


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
        selected_date = timezone.now().date()  # Używamy bieżącej daty
        form = HealthAndCycleForm(initial={'date': selected_date})
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to save the form data.
        """
        form = HealthAndCycleForm(request.POST)  # Tworzymy formularz bez instancji modelu
        if form.is_valid():
            try:
                form.instance.user_profile = request.user.userprofile
                form.instance.recorded_at = timezone.now()
                form.save()
                messages.success(request, "Form saved.")
                return redirect('calendar')  # Zwykłe przekierowanie na stronę kalendarza
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "KO in form.")

        return render(request, self.template_name, {'form': form})


class StatisticsView(LoginRequiredMixin, TemplateView):
    """
    View for displaying statistics related to the user's cycle.
    """
    redirect_field_name = 'next'
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        """
        Adds cycle statistics and related data to the context.
        """
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.StatisticsCycleInfo.userprofile

        try:
            statistics = StatisticsCycleInfo.objects.get(user_profile=user_profile)
            context.update({
                'statistics': statistics,
                'has_data': True,
                'cycle_details': {
                    'first_day_of_cycle': statistics.first_day_of_cycle,
                    'cycle_length': statistics.cycle_length,
                    'period_length': statistics.period_length,
                    'last_period_start': statistics.last_period_start,
                    'average_pain_level': statistics.average_pain_level,
                    'current_cycle_day': statistics.current_cycle_day,
                },
                'phase_details': {
                    'menstruation_phase_start': statistics.menstruation_phase_start,
                    'menstruation_phase_end': statistics.menstruation_phase_end,
                    'menstruation_days': statistics.menstruation_days,
                },
                'health_info': {
                    'allergies': statistics.allergies,
                    'medications': statistics.medications,
                    'health_conditions': statistics.health_conditions,
                },
                'daily_tracking': {
                    'symptoms': statistics.daily_symptoms,
                    'mood': statistics.daily_mood,
                },
                'pregnancy_info': {
                    'pregnancy_start': statistics.pregnancy_start,
                    'pregnancy_end': statistics.pregnancy_end,
                },
                'additional_details': {
                    'date': statistics.date,
                    'event': statistics.event,
                    'recorded_at': statistics.recorded_at,
                }
            })
        except StatisticsCycleInfo.DoesNotExist:
            context['has_data'] = False

        return context


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
