import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from tasks.models import Task, Status


# Create your views here.
def home(request):
    return render(request, 'home.html')


def parse_deadline(deadline_str: str) -> datetime.datetime | None:
    """
    Converts a string YYYY-MM-DD into a datetime object, or None if it's invalid.
    """

    if not deadline_str:
        return None
    try:
        deadline = datetime.datetime.strptime(deadline_str.strip(), "%Y-%m-%d")
        deadline = timezone.make_aware(deadline)

        return deadline
    except ValueError:
        return None


def create_task(request):
    """
    Create a new task or render the creation form.
    """

    if request.method == 'POST':
        name: str = request.POST.get('task-name', '')
        description: str = request.POST.get('task-description', '').strip()
        status_id: Status = Status.objects.get(name='Pendiente')

        deadline_str: str = request.POST.get('task-deadline', '').strip()
        deadline: datetime.datetime = parse_deadline(deadline_str)

        Task.objects.create(
            name=name,
            description=description,
            deadline=deadline,
            status_id=status_id,
        )

        messages.success(request, '¡Tarea creada exitosamente!')

        # return redirect('list-tasks')
        return redirect('home')

    return render(request, 'create_task.html')


def list_tasks(request):
    """
    List all tasks.
    """

    return render(
        request, 
        'list_tasks.html', 
        {
            'tasks': Task.objects.all(),
        },
    )