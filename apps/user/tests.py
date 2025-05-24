from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.serializers import (
    UserSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('user:register')
        self.valid_data = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }

    def test_successful_registration(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_prohibited_username(self):
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'Admin'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This username is prohibited.', str(response.content))

    def test_invalid_username_characters(self):
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'test$user!'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username can contains only letters', str(response.content))

    def test_short_username(self):
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'usr'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ensure this field has at least 4 characters.', str(response.content))

    def test_weak_password(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '1234'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is too short', str(response.content))

    def test_existing_user_registration(self):
        User.objects.create_user(username='existing', password='testpass')
        invalid_data = {'username': 'existing', 'password': 'newpass123'}
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='OldPassword123!'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user:change-password')

    def test_successful_password_change(self):
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewSecurePassword456!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data['new_password']))

    def test_wrong_old_password(self):
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewSecurePassword456!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Old password typed incorrectly.', str(response.content))

    def test_weak_new_password(self):
        data = {
            'old_password': 'OldPassword123!',
            'new_password': '1234'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is too short', str(response.content))

    def test_unauthenticated_access(self):
        self.client.logout()
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewSecurePassword456!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token_url = reverse('user:token_obtain_pair')
        self.refresh_url = reverse('user:token_refresh')

    def test_jwt_token_obtainment(self):
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(self.refresh_url, {
            'refresh': str(refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_credentials(self):
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SerializerValidationTests(APITestCase):
    def test_user_serializer_validation(self):
        data = {'username': ' root ', 'password': 'weak'}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('This username is prohibited.', str(serializer.errors))
        self.assertIn('This password is too short', str(serializer.errors))

    def test_password_change_serializer_validation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        data = {'old_password': 'wrong', 'new_password': '123'}
        serializer = ChangePasswordSerializer(data=data, context={'request': type('', (), {'user': user})()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Old password typed incorrectly.', str(serializer.errors))
        self.assertIn('This password is too short', str(serializer.errors))
