"""
URL configuration for period_tracker_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from period_app.views import RegisterView, LoginView, CustomLogoutView, Home, CalendarView, StatisticsView, \
    KnowledgeBaseView, CycleHealthForm, UserProfileViewSet


router = DefaultRouter()
router.register(r'user-profile', UserProfileViewSet, basename='user_profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', Home.as_view(), name='home'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('knowledge-base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('cycle-health-form/', CycleHealthForm.as_view(), name='form'),
    path('user-profile/', include(router.urls)),
]