from django.urls import path
from .views import routine_view, delete_task

urlpatterns = [
    path('', routine_view, name='routine_home'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
]