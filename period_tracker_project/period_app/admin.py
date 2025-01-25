from django.contrib import admin
from period_app.models import (
    UserProfile,
    StatisticsCycleInfo,
    HealthAndCycleFormModel,
    CustomUser
)

admin.site.register(UserProfile)
admin.site.register(HealthAndCycleFormModel)
admin.site.register(StatisticsCycleInfo)
admin.site.register(CustomUser)