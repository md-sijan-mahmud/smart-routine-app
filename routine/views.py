from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import RoutineItem, UserStreak
from .telegram import send_telegram_message  # Telegram function import kora holo
import json
from django.core.serializers.json import DjangoJSONEncoder

def routine_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description', '')

        # Task toiri kora
        task = RoutineItem.objects.create(
            title=title,
            category=category,
            start_time=start_time,
            end_time=end_time,
            description=description
        )

        # 12-hour format conversion for instant message
        start_12hr = task.start_time.strftime('%I:%M %p') if task.start_time else ""
        end_12hr = task.end_time.strftime('%I:%M %p') if task.end_time else ""

        # Immediate Notification with Buttons: Task add hoilei Telegram-e buttonসহ message jabe
        msg = f"📌 *New Routine Task Added!*\n\n*Task:* {title}\n*Time:* {start_12hr} - {end_12hr}\n*Category:* {category}"
        send_telegram_message(msg, task_id=task.id) # ekhane task_id pass kora holo

        return redirect('routine_home')

    tasks = RoutineItem.objects.all().order_by('start_time')
    
    # --- Productivity Analytics & Streak Calculations ---
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    completion_rate = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    # Streak Logic
    streak_obj, created = UserStreak.objects.get_or_create(pk=1)
    today = timezone.now().date()
    if completion_rate >= 80 and streak_obj.last_updated != today:
        streak_obj.current_streak += 1
        if streak_obj.current_streak > streak_obj.best_streak:
            streak_obj.best_streak = streak_obj.current_streak
        streak_obj.last_updated = today
        streak_obj.save()
    # ---------------------------------------------------

    tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'start_time': task.start_time.strftime('%H:%M')
        }
        for task in tasks
    ]
    tasks_json = json.dumps(tasks_data, cls=DjangoJSONEncoder)

    context = {
        'tasks': tasks,
        'tasks_json': tasks_json,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'streak_count': streak_obj.current_streak,
    }

    return render(request, 'routine/index.html', context)

def delete_task(request, task_id):
    task = get_object_or_404(RoutineItem, id=task_id)
    task.delete()
    return redirect('routine_home')

# --- TELEGRAM WEBHOOK VIEW (Button Click Handler) ---
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if user clicked an inline button
            if 'callback_query' in data:
                callback_query = data['callback_query']
                callback_data = callback_query['data'] # Example: "done_5" ba "snooze_5"
                
                action, task_id = callback_data.split('_')
                task = RoutineItem.objects.filter(id=task_id).first()
                
                if task:
                    if action == 'done':
                        task.is_completed = True
                        task.save()
                    elif action == 'snooze':
                        # Ekhane chaile snooze logic add korte paren
                        pass
        except Exception as e:
            print(f"Webhook Error: {e}")
            
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)