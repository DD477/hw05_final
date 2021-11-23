import shutil
import tempfile
from os import fpathconf

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.another_user = User.objects.create_user(username='AnotherTestUser')
        cls.follower = User.objects.create_user(username='Follower')
        cls.gpoup = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.follow_record = Follow.objects.create(
            author=cls.another_user,
            user=cls.follower,
        )
        cls.another_group = Group.objects.create(
            title='Another group',
            slug='another-slug',
            description='Another description',
        )
        for i in range(14):
            Post.objects.create(
                author=cls.user,
                text='Test text',
                group=cls.gpoup,
            )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.gpoup,
            image=uploaded,
        )
        cls.another_post = Post.objects.create(
            author=cls.another_user,
            text='Another test text',
            group=cls.another_group,
            image=uploaded,
        )
        cls.comments = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Comment text'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guests_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_pages_uses_correct_template(self):
        """View-функции используют правильные html-шаблоны."""
        templates_pages_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.gpoup.slug}'}):
            'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}):
            'posts/profile.html',
        }

        for url, template in templates_pages_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response, template,
                    f'view-функция {url} '
                    'использует неправильный шаблон')

    def test_index_page_show_correct_context(self):
        """View-функция index возвращает корректный context."""
        response = (self.authorized_client.
                    get(reverse('posts:index')))

        post = response.context['page_obj'][1]
        self.assertEqual(post, self.post)

    def test_group_list_page_show_correct_context(self):
        """View-функция group_posts возвращает корректный context."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.gpoup.slug]))

        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].group, self.gpoup)
        self.assertEqual(response.context['group'], self.gpoup)

    def test_profile_page_show_correct_context(self):
        """View-функция profile возвращает корректный context."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username]))
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['count_posts'], 15)
        self.assertEqual(response.context['page_obj'][0].author, self.user)

    def test_post_detail_page_show_correct_context(self):
        """View-функция post_detail возвращает корректный context."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['count_posts'], 15)
        self.assertEqual(response.context['comments'][0], self.comments)

    def test_edit_page_show_correct_context(self):
        """View-функция post_edit возвращает корректный context."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].id, self.post.id)

    def test_create_page_show_correct_context(self):
        """View-функция post_create возвращает корректный context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_index_page_cache(self):
        """Проверка кеширования списка постов на главной странице."""
        content = (self.authorized_client.
                   get(reverse('posts:index')).content)
        Post.objects.filter(id=self.post.id).delete()
        cached_content = (self.authorized_client.
                          get(reverse('posts:index')).content)
        self.assertEqual(content, cached_content)

    def test_index_page_after_clear_cache(self):
        """Проверка обновления списка постов на главной странице
        после очистки кэша."""
        content = (self.authorized_client.
                   get(reverse('posts:index')).content)
        Post.objects.filter(id=self.post.id).delete()
        cache.clear()
        content_after_clear_cache = (self.authorized_client.
                                     get(reverse('posts:index')).content)
        self.assertNotEqual(content, content_after_clear_cache)

    def test_user_follow(self):
        """Авторизованный пользователь может подписываться 
        на других пользователей."""
        count_follow = Follow.objects.count()
        response = self.authorized_follower.get(
            reverse('posts:profile_follow', args=[self.user.username]))
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertTrue(
            Follow.objects.filter(
                author_id=self.user.id,
                user_id=self.follower.id,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username]))

    def test_user_unfollow(self):
        """Авторизованный пользователь может отписаться 
        от других пользователей."""
        count_follow = Follow.objects.count()
        response = self.authorized_follower.get(
            reverse('posts:profile_unfollow',
                    args=[self.another_user.username]))
        self.assertEqual(Follow.objects.count(), count_follow - 1)
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.another_user.username]))

    def test_follower_sees_subscribed_post(self):
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        self.assertEqual(self.another_post, response.context['page_obj'][0])

    def test_follower_dont_sees_not_subscribed_post(self):
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        self.assertNotEqual(self.post, response.context['page_obj'][0])


class PaginatorViewsTest(PostPagesTests):
    def test_first_page_contains_ten_records(self):
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.gpoup.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=1')
                expected = len(response.context['page_obj'])
                self.assertEqual(10, expected,
                                 f'На странице {page} {expected} постов, '
                                 'а не 10')

    def test_second_page_contains_four_records(self):
        pages = {
            reverse('posts:index'): 6,
            reverse('posts:group_list', args=[self.gpoup.slug]): 5,
            reverse('posts:profile', args=[self.user.username]): 5,
        }
        for page, page_count in pages.items():
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                expected = len(response.context['page_obj'])
                self.assertEqual(page_count, expected,
                                 f'На странице {page} {expected} постов, '
                                 f'а не {page_count}')
