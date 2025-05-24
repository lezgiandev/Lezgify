from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from apps.sources.models import Category, Source, MarkedSource
from apps.sources.serializers import MarkedSourceSerializer, SourceSerializer

User = get_user_model()


class ModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Литература')
        self.source = Source.objects.create(
            text='Лезгинская энциклопедия',
            link='https://example.com',
            category=self.category
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Литература')
        self.assertEqual(Category.objects.count(), 1)

    def test_source_creation(self):
        self.assertEqual(str(self.source), 'Лезгинская энциклопедия')
        self.assertEqual(self.source.category.name, 'Литература')

    def test_marked_source_unique(self):
        MarkedSource.objects.create(user=self.user, source=self.source)
        with self.assertRaises(Exception):
            MarkedSource.objects.create(user=self.user, source=self.source)


class SourceAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Фильмы')
        self.source1 = Source.objects.create(
            text='Лезгинские фильмы',
            link='https://movies.com',
            category=self.category
        )
        self.source2 = Source.objects.create(
            text='Документальные фильмы',
            link='https://docs.com',
            category=self.category
        )

    def test_get_sources_list(self):
        url = reverse('sources:source-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_source_filtering(self):
        url = reverse('sources:source-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(len(response.data), 2)

    def test_source_search(self):
        url = reverse('sources:source-list')
        response = self.client.get(url, {'search': 'документальные'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Документальные фильмы')


class MarkedSourceAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='other', password='otherpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Музыка')
        self.source = Source.objects.create(
            text='Лезгинские песни',
            link='https://music.com',
            category=self.category
        )

    def test_add_marked_source(self):
        url = reverse('sources:marked-list')
        data = {'source_id': self.source.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MarkedSource.objects.count(), 1)

    def test_duplicate_marked_source(self):
        MarkedSource.objects.create(user=self.user, source=self.source)
        url = reverse('sources:marked-list')
        data = {'source_id': self.source.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_marked_source(self):
        marked = MarkedSource.objects.create(user=self.user, source=self.source)
        url = reverse('sources:marked-detail', args=[marked.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MarkedSource.objects.count(), 0)

    def test_delete_all_marked_sources(self):
        MarkedSource.objects.create(user=self.user, source=self.source)
        url = reverse('sources:favorite-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MarkedSource.objects.count(), 0)

    def test_foreign_user_access(self):
        other_marked = MarkedSource.objects.create(user=self.other_user, source=self.source)
        url = reverse('sources:marked-detail', args=[other_marked.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SerializerValidationTests(APITestCase):
    def test_source_serializer_validation(self):
        data = {
            'text': '   ',
            'link': '   ',
            'category': 1
        }
        serializer = SourceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Текст источника не может быть пустым!', str(serializer.errors))
        self.assertIn('Адрес ссылки не может быть пустым!', str(serializer.errors))

    def test_marked_source_serializer(self):
        user = User.objects.create_user(username='test', password='test')
        category = Category.objects.create(name='Тест')
        source = Source.objects.create(
            text='Тестовый источник',
            link='https://test.com',
            category=category
        )
        data = {
            'user': user.id,
            'source_id': source.id
        }
        serializer = MarkedSourceSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AuthenticationTests(APITestCase):
    def test_unauthenticated_access(self):
        category = Category.objects.create(name='Тест')
        source = Source.objects.create(
            text='Тест',
            link='https://test.com',
            category=category
        )

        endpoints = [
            reverse('sources:source-list'),
            reverse('sources:marked-list'),
            reverse('sources:category-list')
        ]

        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
