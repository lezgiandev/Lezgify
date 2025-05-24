from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIClient
)
from apps.phrasebook.models import (
    Category,
    Phrase,
    Translation,
    FavoritePhrase,
    LearnedPhrase
)
from apps.phrasebook.serializers import (
    PhraseSerializer,
    TranslationSerializer
)

User = get_user_model()


class ModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Greetings')
        self.phrase = Phrase.objects.create(
            text='Hello',
            category=self.category
        )
        self.translation = Translation.objects.create(
            text='Салам',
            audio='audio.mp3',
            phrase=self.phrase
        )

    def test_phrase_creation(self):
        self.assertEqual(str(self.phrase), 'Hello')
        self.assertEqual(self.phrase.category.name, 'Greetings')

    def test_translation_creation(self):
        self.assertEqual(str(self.translation), 'Hello - Салам')

    def test_favorite_phrase_unique(self):
        FavoritePhrase.objects.create(user=self.user, translation=self.translation)
        with self.assertRaises(Exception):
            FavoritePhrase.objects.create(user=self.user, translation=self.translation)

    def test_learned_phrase_unique(self):
        LearnedPhrase.objects.create(user=self.user, translation=self.translation)
        with self.assertRaises(Exception):
            LearnedPhrase.objects.create(user=self.user, translation=self.translation)


class PhrasebookAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Basic')
        self.phrase1 = Phrase.objects.create(text='Good morning', category=self.category)
        self.phrase2 = Phrase.objects.create(text='Good night', category=self.category)
        self.translation1 = Translation.objects.create(
            text='Руьгьуьд хейр',
            audio='audio1.mp3',
            phrase=self.phrase1
        )
        self.translation2 = Translation.objects.create(
            text='Хъуьрейн хейр',
            audio='audio2.mp3',
            phrase=self.phrase2
        )

    def test_get_phrases_list(self):
        url = reverse('phrasebook:phrase-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_phrase_filtering(self):
        url = reverse('phrasebook:phrase-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(len(response.data), 2)

    def test_phrase_search(self):
        url = reverse('phrasebook:phrase-list')
        response = self.client.get(url, {'search': 'morning'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Good morning')

    def test_phrase_translations_endpoint(self):
        url = reverse('phrasebook:phrase-translations', args=[self.phrase1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['translations']), 1)


class FavoritePhraseAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='other', password='otherpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Food')
        self.phrase = Phrase.objects.create(text='Bread', category=self.category)
        self.translation = Translation.objects.create(
            text='КIару',
            audio='bread.mp3',
            phrase=self.phrase
        )

    def test_add_to_favorites(self):
        url = reverse('phrasebook:favorite-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoritePhrase.objects.count(), 1)

    def test_duplicate_favorite(self):
        FavoritePhrase.objects.create(user=self.user, translation=self.translation)
        url = reverse('phrasebook:favorite-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favorite(self):
        favorite = FavoritePhrase.objects.create(user=self.user, translation=self.translation)
        url = reverse('phrasebook:favorite-detail', args=[favorite.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoritePhrase.objects.count(), 0)

    def test_delete_all_favorites(self):
        FavoritePhrase.objects.create(user=self.user, translation=self.translation)
        url = reverse('phrasebook:favorite-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoritePhrase.objects.count(), 0)


class LearnedPhraseAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Numbers')
        self.phrase = Phrase.objects.create(text='One', category=self.category)
        self.translation = Translation.objects.create(
            text='Са',
            audio='one.mp3',
            phrase=self.phrase
        )

    def test_learn_phrase(self):
        url = reverse('phrasebook:learned-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearnedPhrase.objects.count(), 1)

    def test_get_learned_count(self):
        LearnedPhrase.objects.create(user=self.user, translation=self.translation)
        url = reverse('phrasebook:learned-get-learned-count')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

    def test_delete_learned_phrase(self):
        learned = LearnedPhrase.objects.create(user=self.user, translation=self.translation)
        url = reverse('phrasebook:learned-detail', args=[learned.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LearnedPhrase.objects.count(), 0)

    def test_foreign_user_access(self):
        other_user = User.objects.create_user(username='other', password='pass')
        learned = LearnedPhrase.objects.create(user=other_user, translation=self.translation)
        url = reverse('phrasebook:learned-detail', args=[learned.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SerializerValidationTests(APITestCase):
    def test_phrase_serializer_validation(self):
        data = {'text': '   ', 'category': 1}
        serializer = PhraseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Текст фразы не может быть пустым!', str(serializer.errors))

    def test_translation_serializer_validation(self):
        data = {'text': '   ', 'audio': '   '}
        serializer = TranslationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Текст перевода не может быть пустым!', str(serializer.errors))
        self.assertIn('Аудио перевода не может быть пустым!', str(serializer.errors))
