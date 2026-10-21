from django.contrib.admin import register, ModelAdmin
from .models import RoutineItem

@register(RoutineItem)
class RoutineItemAdmin(ModelAdmin):
    list_display = ('title', 'category', 'start_time', 'end_time', 'is_completed')
    list_filter = ('category', 'is_completed')
    search_fields = ('title', 'description')