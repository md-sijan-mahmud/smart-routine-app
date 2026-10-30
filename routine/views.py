from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import RoutineItem, UserStreak
from .telegram import send_telegram_message  # Telegram function import kora holo
import json
from django.core.serializers.json import DjangoJSONEncoder

# --- 1. Register View ---
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('routine_home')
    else:
        form = UserCreationForm()
    return render(request, 'routine/register.html', {'form': form})

# --- 2. Login View ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('routine_home')
    else:
        form = AuthenticationForm()
    return render(request, 'routine/login.html', {'form': form})

# --- 3. Logout View ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- 4. Main Routine Dashboard View (Multi-user Secured) ---
@login_required(login_url='login')
def routine_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'MEDIUM')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description', '')

        # Task toiri kora ebong logged-in user assign kora
        task = RoutineItem.objects.create(
            user=request.user,
            title=title,
            category=category,
            priority=priority,
            start_time=start_time,
            end_time=end_time,
            description=description
        )

        # 12-hour format conversion for instant message
        start_12hr = task.start_time.strftime('%I:%M %p') if task.start_time else ""
        end_12hr = task.end_time.strftime('%I:%M %p') if task.end_time else ""

        # Immediate Notification with Buttons
        msg = f"📌 *New Routine Task Added!*\n\n*Task:* {title}\n*Time:* {start_12hr} - {end_12hr}\n*Category:* {category}"
        send_telegram_message(msg, task_id=task.id)

        return redirect('routine_home')

    # Shudhu logged-in user-er task-gulo fetch korbe
    tasks = RoutineItem.objects.filter(user=request.user).order_by('start_time')
    
    # --- Productivity Analytics & Streak Calculations (User-specific) ---
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    completion_rate = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    # Streak Logic for current user
    streak_obj, created = UserStreak.objects.get_or_create(user=request.user)
    today = timezone.now().date()
    if completion_rate >= 80 and streak_obj.last_updated != today:
        streak_obj.current_streak += 1
        if streak_obj.current_streak > streak_obj.best_streak:
            streak_obj.best_streak = streak_obj.current_streak
        streak_obj.last_updated = today
        streak_obj.save()

    tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'start_time': task.start_time.strftime('%H:%M') if task.start_time else ""
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

@login_required(login_url='login')
def delete_task(request, task_id):
    task = get_object_or_404(RoutineItem, id=task_id, user=request.user)
    task.delete()
    return redirect('routine_home')

@login_required(login_url='login')
def send_task_telegram(request, task_id):
    task = get_object_or_404(RoutineItem, id=task_id, user=request.user)
    
    start_12hr = task.start_time.strftime('%I:%M %p') if task.start_time else ""
    end_12hr = task.end_time.strftime('%I:%M %p') if task.end_time else ""
    
    msg = f"📌 *Routine Task Reminder!*\n\n*Task:* {task.title}\n*Time:* {start_12hr} - {end_12hr}\n*Category:* {task.get_category_display()}"
    send_telegram_message(msg, task_id=task.id)
    
    return redirect('routine_home')

# --- TELEGRAM WEBHOOK VIEW (Button Click Handler) ---
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if 'callback_query' in data:
                callback_query = data['callback_query']
                callback_data = callback_query['data']
                
                action, task_id = callback_data.split('_')
                task = RoutineItem.objects.filter(id=task_id).first()
                
                if task:
                    if action == 'done':
                        task.is_completed = True
                        task.save()
                    elif action == 'snooze':
                        pass
        except Exception as e:
            print(f"Webhook Error: {e}")
            
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)