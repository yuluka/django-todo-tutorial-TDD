from django.test import TestCase
from .models import Task, Status
import datetime
from django.urls import reverse
from django.utils import timezone

# Create your tests here.


class CreateTaskViewTest(TestCase):
    """
    Test cases for create_task view.
    """

    def setUp(self):
        self.status = Status.objects.create(name="Pendiente")

    def test_create_task(self):
        """
        Test the create_task endpoint.
        """

        response = self.client.post(
            reverse("create-task"),
            {
                "task-name": "Aprender TDD",
                "task-description": "Seguir el tutorial paso a paso",
                "task-deadline": "2025-09-15",
            },
        )

        # Verificamos que la tarea se haya guardado en la BD con la información correcta
        task = Task.objects.first()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Aprender TDD")
        self.assertEqual(task.description, "Seguir el tutorial paso a paso")

        expected_date = timezone.make_aware(datetime.datetime(2025, 9, 15))
        self.assertEqual(task.deadline, expected_date)
        self.assertEqual(task.status_id, self.status)


class ListTasksViewTest(TestCase):
    """
    Test cases for list_tasks view.
    """

    def setUp(self):
        self.status = Status.objects.create(name="Pendiente")

    def test_list_tasks(self):
        """
        Test the list_tasks endpoint.
        """

        # Crear una tarea para listar
        Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status_id=self.status,
        )

        response = self.client.get(reverse("list-tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list_tasks.html")

        # Verificamos que la tarea se muestre en la lista
        self.assertContains(response, "Aprender TDD")
        self.assertContains(response, "Seguir el tutorial paso a paso")
