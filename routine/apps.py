from django.apps import AppConfig
import os

class RoutineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routine'

    def ready(self):
        # Prevent scheduler from running twice during development reload
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime
        from .models import RoutineItem
        from .telegram import send_telegram_message

        def check_routine_reminders():
            now = datetime.now()
            current_time_str = now.strftime('%H:%M')  # e.g., "20:00"
            
            tasks = RoutineItem.objects.filter(start_time=current_time_str)
            for task in tasks:
                # 12-hour format conversion (AM/PM)
                start_12hr = task.start_time.strftime('%I:%M %p')
                end_12hr = task.end_time.strftime('%I:%M %p') if task.end_time else ""
                
                msg = f"⏰ *Routine Reminder!*\n\n*Task:* {task.title}\n*Category:* {task.category}\n*Time:* {start_12hr} - {end_12hr}\n\n*Cholo kaj shuru kore dei! 🚀*"
                send_telegram_message(msg)

        scheduler = BackgroundScheduler()
        # Proti 1 minute por por check korbe
        scheduler.add_job(check_routine_reminders, 'interval', minutes=1)
        scheduler.start()