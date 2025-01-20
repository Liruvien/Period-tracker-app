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

    def get(self, request, *args, **kwargs):
        health_data = HealthAndCycleFormModel.objects.filter(user_profile__user=request.user)
        events = []

        if health_data.exists():
            for entry in health_data:
                if entry.menstruation_phase_start:
                    events.append({
                        'title': 'Menstruacja',
                        'start': entry.menstruation_phase_start.isoformat(),
                        'end': entry.menstruation_phase_end.isoformat(),
                        'color': 'red',
                    })
                if entry.follicular_phase_start:
                    events.append({
                        'title': 'Faza folikularna',
                        'start': entry.follicular_phase_start.isoformat(),
                        'end': entry.follicular_phase_end.isoformat(),
                        'color': 'yellow',
                    })
                if entry.ovulation_phase_start:
                    events.append({
                        'title': 'Owulacja',
                        'start': entry.ovulation_phase_start.isoformat(),
                        'end': entry.ovulation_phase_end.isoformat(),
                        'color': 'green',
                    })
                if entry.luteal_phase_start:
                    events.append({
                        'title': 'Faza lutealna',
                        'start': entry.luteal_phase_start.isoformat(),
                        'end': entry.luteal_phase_end.isoformat(),
                        'color': 'blue',
                    })

        return render(request, self.template_name, {'events': events})

    def calculate_next_period(self, cycle_info):
        if cycle_info.last_period_start and cycle_info.cycle_length:
            next_period = cycle_info.last_period_start + timedelta(days=cycle_info.cycle_length)
            return next_period
        return None

    def calculate_fertile_window(self, cycle_info):
        if cycle_info.last_period_start and cycle_info.cycle_length:
            ovulation_day = cycle_info.last_period_start + timedelta(days=cycle_info.cycle_length - 14)
            fertile_window_start = ovulation_day - timedelta(days=5)
            fertile_window_end = ovulation_day + timedelta(days=1)
            return fertile_window_start, fertile_window_end
        return None, None

    def next_period_prediction(self, cycle_info):
        next_period = self.calculate_next_period(cycle_info)
        if next_period:
            return f"Twoja kolejna miesiączka powinna rozpocząć się {next_period.strftime('%d-%m-%Y')}."
        return "Nie masz wystarczających danych, aby obliczyć przewidywaną datę kolejnej miesiączki."

    def fertile_window_prediction(self, cycle_info):
        fertile_window_start, fertile_window_end = self.calculate_fertile_window(cycle_info)
        if fertile_window_start and fertile_window_end:
            return f"Twój okres płodny przypada od {fertile_window_start.strftime('%d-%m-%Y')} do {fertile_window_end.strftime('%d-%m-%Y')}."
        return "Nie masz wystarczających danych, aby obliczyć przewidywany okres płodny."

    def calculate_phases(self, cycle_info):
        if cycle_info.last_period_start and cycle_info.cycle_length and cycle_info.period_length:
            menstruation_phase_end = cycle_info.last_period_start + timedelta(days=cycle_info.period_length)
            follicular_phase_end = cycle_info.last_period_start + timedelta(days=cycle_info.cycle_length - 14)
            ovulation_phase_start = follicular_phase_end
            luteal_phase_start = follicular_phase_end + timedelta(days=1)
            ovulation_phase_end = ovulation_phase_start
            luteal_phase_end = cycle_info.last_period_start + timedelta(days=cycle_info.cycle_length)

            cycle_info.menstruation_phase_start = cycle_info.last_period_start
            cycle_info.menstruation_phase_end = menstruation_phase_end
            cycle_info.follicular_phase_start = cycle_info.last_period_start
            cycle_info.follicular_phase_end = follicular_phase_end
            cycle_info.ovulation_phase_start = ovulation_phase_start
            cycle_info.ovulation_phase_end = ovulation_phase_end
            cycle_info.luteal_phase_start = luteal_phase_start
            cycle_info.luteal_phase_end = luteal_phase_end
            cycle_info.save()

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