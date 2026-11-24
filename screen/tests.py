import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import MAX_IMAGE_BYTES, PostForm
from .models import Post


def image_file(name, size, image_format):
    buffer = io.BytesIO()
    Image.new('RGB', size, 'blue').save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/bmp')


class AuthHardeningTests(TestCase):
    def test_add_post_requires_login(self):
        response = self.client.get(reverse('add_post'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_login_without_remember_closes_with_the_browser(self):
        User.objects.create_user('ada', password='Correct-horse-battery-9')
        response = self.client.post(reverse('login'), {
            'username': 'ada',
            'password': 'Correct-horse-battery-9',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_remember_keeps_a_two_week_session(self):
        User.objects.create_user('ada', password='Correct-horse-battery-9')
        response = self.client.post(reverse('login'), {
            'username': 'ada',
            'password': 'Correct-horse-battery-9',
            'remember': '1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertGreater(self.client.session.get_expiry_age(), 60 * 60 * 24 * 13)

    def test_only_the_author_can_edit(self):
        author = User.objects.create_user('author', password='Correct-horse-battery-9')
        other = User.objects.create_user('other', password='Correct-horse-battery-9')
        post = Post.objects.create(title='Route', body='Details', author=author)
        self.client.force_login(other)
        response = self.client.post(reverse('edit_post', args=[post.pk]), {
            'title': 'Changed',
            'body': 'Nope',
        })
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Route')


class CommentAndUploadTests(TestCase):
    def test_comment_is_saved_and_honeypot_is_rejected(self):
        post = Post.objects.create(title='Vessel', body='At sea')
        ok = self.client.post(reverse('post_detail', args=[post.pk]), {
            'name': 'Ann',
            'text': 'On schedule.',
        })
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(post.comments.count(), 1)

        blocked = self.client.post(reverse('post_detail', args=[post.pk]), {
            'name': 'Bot',
            'text': 'Buy this.',
            'hp': 'https://spam.example',
        })
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(post.comments.count(), 1)

    def test_oversized_or_odd_image_is_rejected(self):
        huge = image_file('deck.bmp', (1600, 1200), 'BMP')
        self.assertGreater(huge.size, MAX_IMAGE_BYTES)
        form = PostForm(data={'title': 'Ship', 'body': 'Loaded'}, files={'image': huge})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

        small = io.BytesIO()
        Image.new('RGB', (8, 8), 'red').save(small, format='PNG')
        odd = SimpleUploadedFile('note.exe', small.getvalue(), content_type='image/png')
        form = PostForm(data={'title': 'Ship', 'body': 'Loaded'}, files={'image': odd})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
