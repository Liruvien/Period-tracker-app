from django.contrib import admin
from django.urls import path
from period_app.views import RegisterView, LoginView, CustomLogoutView, Home, CalendarView, StatisticsView, KnowledgeBaseView, CycleHealthFormView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', Home.as_view(), name='home'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('knowledge-base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('cycle-health-form-view/', CycleHealthFormView.as_view(), name='form'),
    path('calendar/events/', CalendarView.as_view(), name='calendar_events'),
]