from django.test import TestCase
from rest_framework.test import APIClient

from chats.models import User


class ApiSmokeTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
        )

    def test_list_conversations_returns_200(self):
        response = self.client.get("/api/v1/conversations/")
        self.assertEqual(response.status_code, 200)

