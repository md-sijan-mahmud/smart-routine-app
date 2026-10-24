from django.apps import AppConfig
import os

class RoutineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routine'

    def ready(self):
        # Prevent running during management commands or duplicate processes
        if os.environ.get('RUN_MAIN') == 'false':
            return
        
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime
        from .models import RoutineItem
        from .telegram import send_telegram_message

        def check_routine_reminders():
            try:
                now = datetime.now()
                current_time_str = now.strftime('%H:%M')  # e.g., "21:34"
                
                tasks = RoutineItem.objects.all()
                for task in tasks:
                    if not task.start_time:
                        continue

                    # Safe conversion to string HH:MM
                    if isinstance(task.start_time, str):
                        task_start_str = task.start_time[:5]
                    else:
                        task_start_str = task.start_time.strftime('%H:%M')

                    # Compare current time with task start time
                    if task_start_str == current_time_str:
                        # 12-hour format string safely
                        if isinstance(task.start_time, str):
                            start_12hr = task.start_time
                        else:
                            start_12hr = task.start_time.strftime('%I:%M %p')

                        end_12hr = ""
                        if task.end_time:
                            if isinstance(task.end_time, str):
                                end_12hr = task.end_time
                            else:
                                end_12hr = task.end_time.strftime('%I:%M %p')

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