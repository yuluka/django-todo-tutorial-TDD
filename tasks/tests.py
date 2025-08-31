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

        response = self.client.post(reverse("create-task"), {
            "task-name": "Aprender TDD",
            "task-description": "Seguir el tutorial paso a paso",
            "task-deadline": "2025-09-15",
        })

        # Verificamos que la tarea se haya guardado en la BD con la información correcta
        task = Task.objects.first()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Aprender TDD")
        self.assertEqual(task.description, "Seguir el tutorial paso a paso")

        expected_date = timezone.make_aware(datetime.datetime(2025, 9, 15))
        self.assertEqual(task.deadline, expected_date)
        self.assertEqual(task.status_id, self.status)