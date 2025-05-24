from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIClient
)
from apps.alphabet.models import (
    Letter,
    LearnedLetter
)

User = get_user_model()


class LetterModelTests(APITestCase):
    def setUp(self):
        self.letter = Letter.objects.create(
            letter="A",
            audio="https://example.com/audio.mp3"
        )

    def test_letter_creation(self):
        self.assertEqual(self.letter.letter, "A")
        self.assertEqual(str(self.letter), "A")


class LearnedLetterModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.letter = Letter.objects.create(letter="B", audio="audio.mp3")
        self.learned = LearnedLetter.objects.create(
            user=self.user,
            letter=self.letter
        )

    def test_learned_letter_creation(self):
        self.assertEqual(self.learned.user.username, "testuser")
        self.assertEqual(str(self.learned), "testuser изучил B")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            LearnedLetter.objects.create(
                user=self.user,
                letter=self.letter
            )


class LetterAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.letter1 = Letter.objects.create(letter="C", audio="audio_c.mp3")
        self.letter2 = Letter.objects.create(letter="D", audio="audio_d.mp3")

    def test_get_letters_list(self):
        url = reverse("alphabet:letters-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["letter"], "C")

    def test_unauthenticated_access(self):
        self.client.logout()
        url = reverse("alphabet:letters-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LearnedLetterAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.letter1 = Letter.objects.create(letter="E", audio="audio_e.mp3")
        self.letter2 = Letter.objects.create(letter="F", audio="audio_f.mp3")

        self.learned1 = LearnedLetter.objects.create(
            user=self.user,
            letter=self.letter1
        )
        self.learned2 = LearnedLetter.objects.create(
            user=self.user,
            letter=self.letter2
        )

        self.learned3 = LearnedLetter.objects.create(
            user=self.other_user,
            letter=self.letter1
        )

    def test_get_learned_list(self):
        url = reverse("alphabet:learned-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["letter"]["letter"], "E")

    def test_create_learned_letter(self):
        url = reverse("alphabet:learned-list")
        new_letter = Letter.objects.create(letter="G", audio="audio_g.mp3")
        data = {"letter_id": new_letter.id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearnedLetter.objects.count(), 4)

    def test_duplicate_learned_letter(self):
        url = reverse("alphabet:learned-list")
        data = {"letter_id": self.letter1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_learned_letter(self):
        url = reverse("alphabet:learned-list")
        params = {"letter_id": self.letter1.id}
        response = self.client.delete(url, params)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LearnedLetter.objects.count(), 3)

    def test_delete_all_learned_letters(self):
        url = reverse("alphabet:learned-delete-all")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LearnedLetter.objects.count(), 1)  # other user's remains

    def test_get_learned_count(self):
        url = reverse("alphabet:learned-get-learned-count")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_foreign_user_access(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("alphabet:learned-list")
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["letter"]["letter"], "E")

    def test_delete_nonexistent_letter(self):
        url = reverse("alphabet:learned-list")
        params = {"letter_id": 999}
        response = self.client.delete(url, params)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_all_empty(self):
        self.client.delete(reverse("alphabet:learned-delete-all"))
        url = reverse("alphabet:learned-delete-all")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
