from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIClient
)
from apps.dictionary.models import (
    Category,
    PartOfSpeech,
    Word,
    Origin,
    Translation,
    FavoriteWord,
    LearnedWord
)

User = get_user_model()


class ModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.part_of_speech = PartOfSpeech.objects.create(name='Noun')
        self.word = Word.objects.create(
            text='Test',
            category=self.category,
            part_of_speech=self.part_of_speech
        )
        self.origin = Origin.objects.create(language='English')
        self.translation = Translation.objects.create(
            text='Translation',
            audio='audio.mp3',
            word=self.word,
            origin=self.origin
        )

    def test_model_creation(self):
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(str(self.part_of_speech), 'Noun')
        self.assertEqual(str(self.word), 'Test')
        self.assertEqual(str(self.origin), 'English')
        self.assertEqual(str(self.translation), 'Test - Translation')

    def test_favorite_word_model(self):
        favorite = FavoriteWord.objects.create(user=self.user, translation=self.translation)
        self.assertEqual(str(favorite), 'testuser - Translation')

        with self.assertRaises(Exception):
            FavoriteWord.objects.create(user=self.user, translation=self.translation)

    def test_learned_word_model(self):
        learned = LearnedWord.objects.create(user=self.user, translation=self.translation)
        self.assertEqual(str(learned), 'testuser - Translation')

        with self.assertRaises(Exception):
            LearnedWord.objects.create(user=self.user, translation=self.translation)


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        Category.objects.create(name='Animals')
        Category.objects.create(name='Food')

    def test_get_categories(self):
        url = reverse('dictionary:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Animals')


class DictionaryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.pos = PartOfSpeech.objects.create(name='Verb')
        self.word1 = Word.objects.create(
            text='Run',
            category=self.category,
            part_of_speech=self.pos
        )
        self.word2 = Word.objects.create(
            text='Jump',
            category=self.category,
            part_of_speech=self.pos
        )

    def test_get_words_list(self):
        url = reverse('dictionary:word-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_word_filtering(self):
        url = reverse('dictionary:word-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(len(response.data), 2)

        new_category = Category.objects.create(name='New Category')
        response = self.client.get(url, {'category': new_category.id})
        self.assertEqual(len(response.data), 0)

    def test_word_search(self):
        url = reverse('dictionary:word-list')
        response = self.client.get(url, {'search': 'Run'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Run')

    def test_word_translations_endpoint(self):
        origin = Origin.objects.create(language='English')
        translation = Translation.objects.create(
            text='Run translation',
            audio='audio.mp3',
            word=self.word1,
            origin=origin
        )

        url = reverse('dictionary:word-translations', args=[self.word1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['translations']), 1)
        self.assertEqual(response.data['word']['text'], 'Run')


class FavoriteWordAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='other', password='otherpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test')
        self.pos = PartOfSpeech.objects.create(name='Noun')
        self.word = Word.objects.create(
            text='Book',
            category=self.category,
            part_of_speech=self.pos
        )
        self.origin = Origin.objects.create(language='English')
        self.translation = Translation.objects.create(
            text='Book translation',
            audio='audio.mp3',
            word=self.word,
            origin=self.origin
        )

    def test_add_to_favorites(self):
        url = reverse('dictionary:favorite-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteWord.objects.count(), 1)

    def test_duplicate_favorite(self):
        FavoriteWord.objects.create(user=self.user, translation=self.translation)
        url = reverse('dictionary:favorite-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favorite(self):
        favorite = FavoriteWord.objects.create(user=self.user, translation=self.translation)
        url = reverse('dictionary:favorite-list')
        response = self.client.delete(url, {'translation_id': self.translation.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteWord.objects.count(), 0)

    def test_delete_all_favorites(self):
        FavoriteWord.objects.create(user=self.user, translation=self.translation)
        url = reverse('dictionary:favorite-delete-all')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteWord.objects.count(), 0)


class LearnedWordAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test')
        self.pos = PartOfSpeech.objects.create(name='Verb')
        self.word = Word.objects.create(
            text='Write',
            category=self.category,
            part_of_speech=self.pos
        )
        self.origin = Origin.objects.create(language='English')
        self.translation = Translation.objects.create(
            text='Write translation',
            audio='audio.mp3',
            word=self.word,
            origin=self.origin
        )

    def test_learn_word(self):
        url = reverse('dictionary:learned-list')
        data = {'translation_id': self.translation.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearnedWord.objects.count(), 1)

    def test_get_learned_count(self):
        LearnedWord.objects.create(user=self.user, translation=self.translation)
        url = reverse('dictionary:learned-get-learned-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_delete_learned_word(self):
        LearnedWord.objects.create(user=self.user, translation=self.translation)
        url = reverse('dictionary:learned-list')
        response = self.client.delete(url, {'translation_id': self.translation.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LearnedWord.objects.count(), 0)

    def test_foreign_user_access(self):
        other_user = User.objects.create_user(username='other', password='otherpass')
        LearnedWord.objects.create(user=other_user, translation=self.translation)
        response = self.client.get(reverse('dictionary:learned-list'))
        self.assertEqual(len(response.data), 0)


class TranslationValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_empty_field_validations(self):
        response = self.client.post(
            reverse('dictionary:category-list'),
            {'name': '   '}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('dictionary:part-of-speech-list'),
            {'name': '   '}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
