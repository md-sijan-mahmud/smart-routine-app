from django.shortcuts import render, redirect, get_object_or_404
from .models import RoutineItem
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

        # Immediate Test Notification: Task add hoilei Telegram-e message jabe
        msg = f"📌 *New Routine Task Added!*\n\n*Task:* {title}\n*Time:* {start_12hr} - {end_12hr}\n*Category:* {category}"
        send_telegram_message(msg)

        return redirect('routine_home')

    tasks = RoutineItem.objects.all().order_by('start_time')
    tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'start_time': task.start_time.strftime('%H:%M')
        }
        for task in tasks
    ]
    tasks_json = json.dumps(tasks_data, cls=DjangoJSONEncoder)

    return render(request, 'routine/index.html', {'tasks': tasks, 'tasks_json': tasks_json})

def delete_task(request, task_id):
    task = get_object_or_404(RoutineItem, id=task_id)
    task.delete()
    return redirect('routine_home')