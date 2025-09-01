import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from tasks.models import Task, Status
from django.core.mail import send_mail


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

        return redirect('list-tasks')

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


def edit_task(request, task_id):
    """
    Edit an existing task or render the edit form.
    """

    if request.method == 'POST':
        task: Task = Task.objects.get(id=task_id)

        task.name = request.POST.get('task-name', '')
        task.description = request.POST.get('task-description', '').strip()
        task.status_id = Status.objects.get(id=int(request.POST.get('task-status', 0)))

        deadline_str: str = request.POST.get('task-deadline', '').strip()
        deadline: datetime.datetime = parse_deadline(deadline_str)

        task.deadline = deadline
        task.save()

        messages.success(request, '¡Tarea actualizada exitosamente!')

        return redirect('list-tasks')

    return render(
        request, 
        'edit_task.html', 
        {
            'task': Task.objects.get(id=task_id),
            'task_statuses': Status.objects.all(),
        }
    )


def delete_task(request, task_id):
    """
    Delete an existing task.
    """

    Task.objects.get(id=task_id).delete()

    messages.success(request, '¡Tarea eliminada exitosamente!')

    return redirect('list-tasks')


def send_email_view(request):
    """
    Send an email or render the email form.
    """
    
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        recipient = request.POST.get('recipient', '')

        if subject and message and recipient:
            try:
                send_mail(subject, message, 'tu_correo@gmail.com', [recipient])

                messages.success(request, '¡Correo enviado exitosamente!')

            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {e}')

        else:
            messages.error(request, 'Todos los campos son obligatorios.')

        return redirect('send-email')

    return render(request, 'send_email.html')