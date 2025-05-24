from django.contrib.auth import get_user_model
from apps.library.serializers import BookmarkSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIClient
)
from apps.library.models import (
    Book,
    Category,
    Sentence,
    Bookmark
)

User = get_user_model()


class BookmarkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category')
        self.book = Book.objects.create(
            title='Test Book',
            author='Author',
            category=self.category,
            logo='logo.jpg'
        )
        self.sentence1 = Sentence.objects.create(
            text='Sentence 1',
            audio='audio1.mp3',
            translate='Translate 1',
            book=self.book
        )
        self.sentence2 = Sentence.objects.create(
            text='Sentence 2',
            audio='audio2.mp3',
            translate='Translate 2',
            book=self.book
        )

    def test_create_bookmark(self):
        url = reverse('library:bookmark-list')
        data = {
            'book_id': self.book.id,
            'sentence_id': self.sentence1.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_replace_bookmark(self):
        Bookmark.objects.create(
            user=self.user,
            book=self.book,
            sentence=self.sentence1
        )

        url = reverse('library:bookmark-list')
        data = {
            'book_id': self.book.id,
            'sentence_id': self.sentence2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)
        self.assertEqual(Bookmark.objects.first().sentence, self.sentence2)

    def test_delete_bookmark(self):
        bookmark = Bookmark.objects.create(
            user=self.user,
            book=self.book,
            sentence=self.sentence1
        )
        url = reverse('library:bookmark-detail', args=[bookmark.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_delete_all_bookmarks(self):
        Bookmark.objects.create(
            user=self.user,
            book=self.book,
            sentence=self.sentence1
        )
        url = reverse('library:bookmark-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_bookmark_unique_constraint(self):
        data = {
            'book_id': self.book.id,
            'sentence_id': self.sentence1.id
        }
        self.client.post(reverse('library:bookmark-list'), data)
        response = self.client.post(reverse('library:bookmark-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with self.assertRaises(Exception):
            Bookmark.objects.create(
                user=self.user,
                book=self.book,
                sentence=self.sentence1
            )

    def test_bookmark_foreign_user_access(self):
        other_user = User.objects.create_user(username='other', password='pass')
        bookmark = Bookmark.objects.create(
            user=other_user,
            book=self.book,
            sentence=self.sentence1
        )

        url = reverse('library:bookmark-detail', args=[bookmark.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookmarkSerializerTests(APITestCase):
    def test_validation(self):
        user = User.objects.create_user(username='test', password='test')
        category = Category.objects.create(name='Test')
        book = Book.objects.create(
            title='Book',
            author='Author',
            category=category,
            logo='logo.jpg'
        )
        sentence = Sentence.objects.create(
            text='Text',
            audio='audio.mp3',
            translate='Translate',
            book=book
        )

        data = {
            'user': user.id,
            'book_id': book.id,
            'sentence_id': sentence.id
        }

        serializer = BookmarkSerializer(data=data)
        self.assertTrue(serializer.is_valid())
