from django.apps import AppConfig
import os

class RoutineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routine'

    def ready(self):
        # Prevent running during manage.py commands or secondary worker processes
        if os.environ.get('RUN_MAIN') == 'false':
            return
        
        from apscheduler.schedulers.background import BackgroundScheduler
        from datetime import datetime, time
        from .models import RoutineItem
        from .telegram import send_telegram_message

        def check_routine_reminders():
            try:
                now = datetime.now()
                current_time_str = now.strftime('%H:%M')  # e.g., "22:05"
                
                tasks = RoutineItem.objects.all()
                for task in tasks:
                    if not task.start_time:
                        continue

                    # Safe string conversion for start_time
                    if isinstance(task.start_time, (datetime, time)):
                        task_start_str = task.start_time.strftime('%H:%M')
                    else:
                        task_start_str = str(task.start_time)[:5]

                    # Match current time with task start time
                    if task_start_str == current_time_str:
                        # Safe formatting for 12-hour start time display
                        if isinstance(task.start_time, (datetime, time)):
                            start_12hr = task.start_time.strftime('%I:%M %p')
                        else:
                            start_12hr = str(task.start_time)

                        # Safe formatting for 12-hour end time display
                        end_12hr = ""
                        if task.end_time:
                            if isinstance(task.end_time, (datetime, time)):
                                end_12hr = task.end_time.strftime('%I:%M %p')
                            else:
                                end_12hr = str(task.end_time)

                        time_text = f"{start_12hr} - {end_12hr}" if end_12hr else start_12hr
                        
                        msg = f"⏰ *Routine Reminder!*\n\n*Task:* {task.title}\n*Category:* {task.category}\n*Time:* {time_text}\n\n*Cholo kaj shuru kore dei! 🚀*"
                        send_telegram_message(msg)
            except Exception as e:
                print(f"Error checking routine reminders: {e}")

        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(check_routine_reminders, 'interval', minutes=1)
            scheduler.start()
            print("🚀 APScheduler started successfully for Telegram reminders!")
        except Exception as e:
            print(f"Failed to start APScheduler: {e}")