from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rating_site.models import Game, Review
from datetime import date


class ReviewViewsTest(TestCase):
    """Один основной тест для представлений отзывов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.game = Game.objects.create(
            name="Тестовая игра",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )
        self.add_review_url = reverse('add_review', args=[self.game.id])

    def test_add_review_redirect_if_not_logged_in(self):
        """Тест: Неавторизованный пользователь не может добавить отзыв"""
        response = self.client.get(self.add_review_url)
        self.assertEqual(response.status_code, 302)  # Редирект на логин
        self.assertIn('/login/', response.url)


class ProfileViewTest(TestCase):
    """Один основной тест для профиля"""

    def test_profile_url_exists(self):
        """Тест: URL профиля существует"""
        # Даже не проверяем содержимое, просто что URL правильный
        url = reverse('profile', args=["testuser"])
        self.assertEqual(url, '/profile/testuser/')