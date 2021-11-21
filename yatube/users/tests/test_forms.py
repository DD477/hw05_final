from unittest.case import skip

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


@skip
class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает нового пользователя в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'username': 'UserName',
            'email': 'test@email.com',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                username=form_data['username'],
                email=form_data['email'],
            ).exists()
        )
