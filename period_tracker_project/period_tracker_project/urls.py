from django.contrib import admin
from django.urls import path
from period_app.views import (
    RegisterView,
    LoginView,
    Home,
    CalendarView,
    StatisticsView,
    KnowledgeBaseView,
    CycleHealthFormView,
    HormonalHealthView,
    DietImpactView,
    SelfCareDuringMenstruationView,
    HealthDuringPregnancyView,
    ExportStatisticsPDFView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', Home.as_view(), name='home'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('statistics/export/pdf/', ExportStatisticsPDFView.as_view(), name='export_statistics_pdf'),
    path('knowledge-base/', KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('cycle-health-form-view/', CycleHealthFormView.as_view(), name='form'),
    path('hormonalne-zdrowie/', HormonalHealthView.as_view(), name='hormonal_health'),
    path('dieta-wplywajaca-pozytywnie-na-kobiece-hormony/', DietImpactView.as_view(), name='diet_impact'),
    path('zaopiekuj-sie-soba-podczas-miesiaczki/', SelfCareDuringMenstruationView.as_view(), name='self_care_menstruation'),
    path('zdrowie-kobiet-podczas-ciazy/', HealthDuringPregnancyView.as_view(), name='health_during_pregnancy'),
]
