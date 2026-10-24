from django.apps import AppConfig
import os

class RoutineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routine'

    def ready(self):
        # Production (Render / Gunicorn) and Local Dev fix
        if os.environ.get('RUN_MAIN') == 'false':
            return
        
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime
        from .models import RoutineItem
        from .telegram import send_telegram_message

        def check_routine_reminders():
            try:
                now = datetime.now()
                # Time object comparison fix
                current_time = now.time().replace(second=0, microsecond=0)
                current_time_str = now.strftime('%H:%M')
                
                # Filter matching tasks
                tasks = RoutineItem.objects.all()
                for task in tasks:
                    # Convert task start_time to HH:MM format safely
                    task_start_str = ""
                    if hasattr(task.start_time, 'strftime'):
                        task_start_str = task.start_time.strftime('%H:%M')
                    else:
                        task_start_str = str(task.start_time)[:5]
                    
                    if task_start_str == current_time_str:
                        # Format 12-hour display time
                        if hasattr(task.start_time, 'strftime'):
                            start_12hr = task.start_time.strftime('%I:%M %p')
                        else:
                            start_12hr = str(task.start_time)

                        end_12hr = ""
                        if task.end_time:
                            if hasattr(task.end_time, 'strftime'):
                                end_12hr = task.end_time.strftime('%I:%M %p')
                            else:
                                end_12hr = str(task.end_time)

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