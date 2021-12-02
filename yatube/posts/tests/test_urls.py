from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='FirstTestUser')
        cls.second_user = User.objects.create_user(username='SecondTestUser')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.first_users_post = Post.objects.create(
            author=cls.first_user,
            text='Some test text',
            group=cls.group
        )
        cls.second_users_post = Post.objects.create(
            author=cls.second_user,
            text='Test text',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.first_user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.first_user}/': 'posts/profile.html',
            f'/posts/{self.first_users_post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.first_users_post.id}/edit/':
            'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response, template,
                    f'Адрес {address} несоответствует шаблону {template}')

    def test_urls_access_for_all_users(self):
        """Страницы доступны любому пользователю."""
        urls = ['/', f'/group/{self.group.slug}/',
                     f'/profile/{self.first_user.username}/',
                     f'/posts/{self.first_users_post.id}/']

        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 f'Адрес {address} '
                                 f'возвращает не код {HTTPStatus.OK}'
                                 )

    def test_create_url_access_for_authorized_user(self):
        """Страница /create/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_access_for_author(self):
        """Страница /posts/<post_id>/edit/ доступна автору."""
        response = self.authorized_client.get(
            f'/posts/{self.first_users_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.first_users_post.author, self.first_user)

    def test_unexisting_page_return_not_found(self):
        """Запрос к несуществующей странице возвращает код 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(
            response, 'core/404.html')

    def test_urls_not_access_for_guest_user(self):
        """Страницы недоступны неавторизованному пользователю."""
        urls = [
            '/create/',
            f'/posts/{self.first_users_post.id}/edit/',
            f'/posts/{self.first_users_post.id}/comment/'
        ]

        for url in urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.FOUND,
                             f'{response.status_code} для {url}')

    def test_post_editing_not_access_for_not_author(self):
        """Страница /posts/<post_id>/edit/ недоступна не автору."""
        response = self.authorized_client.get(
            f'/posts/{self.second_users_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(self.second_users_post.author, self.first_user)
