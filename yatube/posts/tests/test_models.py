import textwrap as tw

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Very long test text',
        )

    def test_group_have_correct_object_names(self):
        """Проверяем, что у модели group корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(str(self.group), expected_object_name)

    def test_post_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        expected_object_name = tw.shorten(
            self.post.text, 15, placeholder='...')
        self.assertEqual(str(self.post), expected_object_name)

#добавить проверку моделей Comment, Follow