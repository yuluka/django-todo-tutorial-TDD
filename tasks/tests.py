from django.test import TestCase
from .models import Task, Status
import datetime
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.contrib.auth.models import User

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


class EditTaskViewTest(TestCase):
    """
    Test cases for edit_tasks view.
    """

    def setUp(self):
        self.status = Status.objects.create(name="Pendiente")
        
        self.task = Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status_id=self.status,
        )

    def test_edit_task(self):
        """
        Test the edit_task endpoint.
        """

        response = self.client.post(
            reverse("edit-task", args=[self.task.id]),
            {
                "task-name": "Aprender TDD - Modificado",
                "task-description": "Seguir el tutorial paso a paso - Modificado",
                "task-deadline": "2025-09-16",
                "task-status": self.status.id,
            },
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Aprender TDD - Modificado")
        self.assertEqual(self.task.description, "Seguir el tutorial paso a paso - Modificado")
        self.assertEqual(self.task.deadline, timezone.make_aware(datetime.datetime(2025, 9, 16)))


class DeleteTaskViewTest(TestCase):
    """
    Test cases for delete_task view.
    """

    def setUp(self):
        self.status = Status.objects.create(name="Pendiente")
        
        self.task = Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status_id=self.status,
        )

    def test_delete_task(self):
        """
        Test the delete_task endpoint.
        """

        response = self.client.post(
            reverse("delete-task", args=[self.task.id])
        )

        # Verificamos que la tarea haya sido eliminada
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class SendEmailViewTest(TestCase):
    """
    Test cases for send_email view.
    """

    def test_send_email(self):
        """
        Test the send_email endpoint.
        """

        response = self.client.post(reverse("send-email"), {
            "subject": "Prueba TDD",
            "message": "Este es un mensaje de prueba",
            "recipient": "un_correo@gmail.com",
        })

        # Verificamos que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Prueba TDD")
        self.assertEqual(mail.outbox[0].body, "Este es un mensaje de prueba")
        self.assertIn("un_correo@gmail.com", mail.outbox[0].to)


class AuthViewsTest(TestCase):
    """
    Test cases for authentication views (login and logout).
    """
    
    def setUp(self):
        # Usuario de prueba
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": self.password
        })

        # Verificar que el usuario esté autenticado en la sesión
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": "wrongpass"
        })

        # No debe redirigir, debe quedarse en login
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos")

        # Verificar que no haya sesión activa
        self.assertFalse("_auth_user_id" in self.client.session)
