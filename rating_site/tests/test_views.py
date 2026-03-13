from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rating_site.models import Game
from datetime import date


class HomeViewTest(TestCase):
    """Тесты для главной страницы"""

    def setUp(self):
        self.client = Client()
        # Создаем игру с уникальным названием
        Game.objects.create(
            name=f"Игра для теста {date.today()}",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

    def test_1_home_page_status(self):
        """Тест 1: Главная страница доступна"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_2_home_page_uses_correct_template(self):
        """Тест 2: Используется правильный шаблон"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')


class GameDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(
            name="Детальная игра",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

    def test_3_game_detail_status(self):
        response = self.client.get(reverse('game_detail', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)


class ReviewViewTest(TestCase):
    """Тесты для отзывов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="reviewer", password="pass123")
        self.game = Game.objects.create(
            name="Игра для отзывов",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )
        self.add_review_url = reverse('add_review', args=[self.game.id])

    def test_4_add_review_redirect_if_not_logged(self):
        """Тест 4: Неавторизованный не может добавить отзыв"""
        response = self.client.get(self.add_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_5_add_review_logged_user_can_access(self):
        """Тест 5: Авторизованный может открыть страницу добавления"""
        self.client.login(username="reviewer", password="pass123")
        response = self.client.get(self.add_review_url)
        self.assertEqual(response.status_code, 200)