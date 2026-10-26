from django.urls import path
from .views import routine_view, delete_task, telegram_webhook, send_task_telegram

urlpatterns = [
    path('', routine_view, name='routine_home'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
    path('send-telegram/<int:task_id>/', send_task_telegram, name='send_telegram'),
    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),
]