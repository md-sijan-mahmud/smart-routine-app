from django.apps import AppConfig
import os

class RoutineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routine'

    def ready(self):
        # Production (Render / Gunicorn) and Local Dev fix
        # Local runserver checks RUN_MAIN to avoid duplicate scheduler jobs
        # In production (Gunicorn), RUN_MAIN is not set, so we execute directly
        if os.environ.get('RUN_MAIN') == 'false':
            return
        
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime
        from .models import RoutineItem
        from .telegram import send_telegram_message

        def check_routine_reminders():
            try:
                now = datetime.now()
                current_time_str = now.strftime('%H:%M')  # e.g., "20:00"
                
                # Fetch tasks that match the current time
                tasks = RoutineItem.objects.filter(start_time=current_time_str)
                for task in tasks:
                    start_12hr = task.start_time.strftime('%I:%M %p') if hasattr(task.start_time, 'strftime') else str(task.start_time)
                    end_12hr = task.end_time.strftime('%I:%M %p') if task.end_time and hasattr(task.end_time, 'strftime') else str(task.end_time or "")
                    
                    time_text = f"{start_12hr} - {end_12hr}" if end_12hr else start_12hr
                    
                    msg = f"⏰ *Routine Reminder!*\n\n*Task:* {task.title}\n*Category:* {task.category}\n*Time:* {time_text}\n\n*Cholo kaj shuru kore dei! 🚀*"
                    send_telegram_message(msg)
            except Exception as e:
                print(f"Error checking routine reminders: {e}")

        scheduler = BackgroundScheduler()
        # Proti 1 minute por por check korbe
        scheduler.add_job(check_routine_reminders, 'interval', minutes=1)
        scheduler.start()
        print("🚀 APScheduler started successfully for Telegram reminders!")