from http import HTTPStatus

from django.test import Client, TestCase


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(
                    response, template,
                    f'Адрес {adress} несоответствует шаблону {template}')

    def test_urls_access_for_all_users(self):
        """Страницы доступны."""
        url_names = ['/auth/signup/', '/auth/login/', '/auth/logout/', ]

        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 f'{response.status_code} для адреса {adress}')
