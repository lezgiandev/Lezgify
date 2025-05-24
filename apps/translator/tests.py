from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import base64

User = get_user_model()


class TranslatorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.translate_url = reverse('translator:translate-tts')
        self.tts_only_url = reverse('translator:tts-only')

    def test_translate_and_tts_success(self):
        data = {'text': 'Доброе утро'}
        response = self.client.post(self.translate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('translation', response.data)
        self.assertIn('audio', response.data)

        audio_data = base64.b64decode(response.data['audio'])
        self.assertTrue(len(audio_data) > 1000)

    def test_tts_only_success(self):
        data = {'lezgin_text': 'Руьгьуьд хейр'}
        response = self.client.post(self.tts_only_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('audio', response.data)

        audio_data = base64.b64decode(response.data['audio'])
        self.assertTrue(len(audio_data) > 1000)

    def test_missing_text_parameter(self):
        response = self.client.post(self.translate_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.tts_only_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_gradio_connection_errors(self):
        data = {'text': ''}
        response = self.client.post(self.translate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'lezgin_text': ''}
        response = self.client.post(self.tts_only_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        self.client.logout()

        response = self.client.post(self.translate_url, {'text': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.tts_only_url, {'lezgin_text': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_audio_generation_failure(self):
        data = {'lezgin_text': '#' * 1000}
        response = self.client.post(self.tts_only_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('TTS Error', response.data['error'])


class SerializerValidationTests(APITestCase):
    def test_input_validation(self):
        client = APIClient()
        user = User.objects.create_user(username='test', password='test')
        client.force_authenticate(user=user)

        long_text = 'a' * 1001
        response = client.post(
            reverse('translator:translate-tts'),
            {'text': long_text},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
