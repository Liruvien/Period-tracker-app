from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from period_app.forms import UserRegisterForm, UserLoginForm
from rest_framework import generics
from period_app.models import UserProfile
from period_app.serializers import UserProfileSerializer
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets


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


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class Home(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'home.html'

    def get(self, request):
        return render(request, "home.html")


class CalendarView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'calendar.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class StatisticsView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'statistics.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class KnowledgeBaseView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'knowledge_base.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CycleHealthForm(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'form.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)