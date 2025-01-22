from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserLoginForm, HealthAndCycleForm
from .models import HealthAndCycleFormModel, StatisticsCycleInfo
from django.utils.dateparse import parse_date
from datetime import timedelta

class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Wrong username or password.')
            return self.form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class Home(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'home.html'

    def get(self, request):
        return render(request, self.template_name)


class CalendarView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        health_form = HealthAndCycleFormModel.objects.filter(user_profile=self.request.user.userprofile).first()
        context['health_form'] = health_form
        context['form'] = HealthAndCycleForm(instance=health_form) if health_form else HealthAndCycleForm()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        date_str = request.POST.get('date')
        selected_date = parse_date(date_str) if date_str else None

        health_form, created = HealthAndCycleFormModel.objects.get_or_create(
            user_profile=request.user.userprofile,
            defaults={'cycle_length': 28, 'period_length': 5}
        )

        if action == "set_menstruation":
            if selected_date:
                health_form.last_period_start = selected_date
                health_form.period_length = int(request.POST.get('period_length', 5))
                health_form.menstruation_days = [
                    (selected_date + timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(health_form.period_length)
                ]
                CycleCalculator.calculate_phases(health_form)
                health_form.save()

        elif action == "edit_menstruation":
            menstruation_days = request.POST.getlist('menstruation_days[]')
            if not menstruation_days:
                health_form.menstruation_days = []
                health_form.last_period_start = None
                health_form.period_length = None
            else:
                health_form.menstruation_days = menstruation_days
                dates = [parse_date(day) for day in menstruation_days]
                health_form.last_period_start = min(dates)
                health_form.period_length = len(dates)

            if health_form.last_period_start:
                CycleCalculator.calculate_phases(health_form)
            else:
                health_form.menstruation_phase_start = None
                health_form.menstruation_phase_end = None
                health_form.follicular_phase_start = None
                health_form.follicular_phase_end = None
                health_form.ovulation_phase_start = None
                health_form.ovulation_phase_end = None
                health_form.luteal_phase_start = None
                health_form.luteal_phase_end = None

            health_form.save()

        elif action == "set_pregnancy":
            if selected_date:
                health_form.pregnancy_start = selected_date
                health_form.pregnancy_end = selected_date + timedelta(days=280)
                health_form.menstruation_phase_start = None
                health_form.menstruation_phase_end = None
                health_form.follicular_phase_start = None
                health_form.follicular_phase_end = None
                health_form.ovulation_phase_start = None
                health_form.ovulation_phase_end = None
                health_form.luteal_phase_start = None
                health_form.luteal_phase_end = None
                health_form.menstruation_days = []
                health_form.last_period_start = None
                health_form.period_length = None
                health_form.save()

        elif action == "remove_pregnancy":
            health_form.pregnancy_start = None
            health_form.pregnancy_end = None
            if health_form.last_period_start:
                CycleCalculator.calculate_phases(health_form)
            health_form.save()

        return redirect('calendar')

class CycleCalculator:
    @staticmethod
    def calculate_phases(health_form):
        if not health_form.last_period_start or not health_form.cycle_length or not health_form.period_length:
            return False

        start = health_form.last_period_start

        health_form.menstruation_days = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                                         range(health_form.period_length)]

        health_form.menstruation_phase_start = start
        health_form.menstruation_phase_end = start + timedelta(days=health_form.period_length - 1)

        follicular_phase_start = health_form.menstruation_phase_end + timedelta(days=1)
        follicular_phase_end = follicular_phase_start + timedelta(days=health_form.cycle_length - health_form.period_length - 14)

        ovulation_phase_start = follicular_phase_end + timedelta(days=1)
        ovulation_phase_end = ovulation_phase_start + timedelta(days=2)

        luteal_phase_start = ovulation_phase_end + timedelta(days=1)
        luteal_phase_end = start + timedelta(days=health_form.cycle_length - 1)

        health_form.follicular_phase_start = follicular_phase_start
        health_form.follicular_phase_end = follicular_phase_end

        health_form.ovulation_phase_start = ovulation_phase_start
        health_form.ovulation_phase_end = ovulation_phase_end

        health_form.luteal_phase_start = luteal_phase_start
        health_form.luteal_phase_end = luteal_phase_end

        health_form.menstruation_days = []

        if health_form.last_period_start and health_form.period_length:
            for i in range(health_form.period_length):
                health_form.menstruation_days.append(health_form.last_period_start + timedelta(days=i))

        health_form.save()
        return True

class StatisticsView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'statistics.html'

    def get(self, request, *args, **kwargs):
        statistics = StatisticsCycleInfo.objects.filter(user_profile__user=request.user)
        has_data = statistics.exists()

        context = {
            'statistics': statistics,
            'has_data': has_data,
        }
        return render(request, self.template_name, context)


class KnowledgeBaseView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'knowledge_base.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class HormonalHealthView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'hormonal_health.html'

    def get(self, request):
        return render(request, self.template_name)


class DietImpactView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'diet_impact.html'

    def get(self, request):
        return render(request, self.template_name)


class SelfCareDuringMenstruationView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'self_care_menstruation.html'

    def get(self, request):
        return render(request, self.template_name)


class HealthDuringPregnancyView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'health_during_pregnancy.html'

    def get(self, request):
        return render(request, self.template_name)


class CycleHealthFormView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'form.html'

    def get(self, request, *args, **kwargs):
        form = HealthAndCycleForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = HealthAndCycleForm(request.POST)

        if form.is_valid():
            health_cycle_data = form.save(commit=False)
            health_cycle_data.user_profile = request.user.userprofile
            health_cycle_data.save()
            return redirect('calendar')
        return render(request, self.template_name, {'form': form})