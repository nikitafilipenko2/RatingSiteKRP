from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rating_site.models import Game, Review, FavouriteGame, Profile
from datetime import date


class UserRegistrationIntegrationTest(TestCase):
    """Интеграционные тесты для регистрации"""

    def setUp(self):
        self.client = Client()

    def test_1_registration_creates_user_and_profile(self):
        """Тест 1: Регистрация создает пользователя и профиль"""
        register_data = {
            'username': 'newuser',
            'password1': 'complex123',
            'password2': 'complex123'
        }
        response = self.client.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 302)

        # Проверяем создание пользователя
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)

        # Проверяем создание профиля
        profile = Profile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)

    def test_2_registration_redirects_to_login(self):
        """Тест 2: После регистрации редирект на страницу входа"""
        register_data = {
            'username': 'newuser2',
            'password1': 'complex123',
            'password2': 'complex123'
        }
        response = self.client.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))


class LoginLogoutIntegrationTest(TestCase):
    """Интеграционные тесты для входа/выхода"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_3_login_success(self):
        """Тест 3: Успешный вход в систему"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Редирект после входа

        # Проверяем, что пользователь действительно вошел (следующий запрос успешен)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_4_logout_works(self):
        """Тест 4: Выход из системы"""
        self.client.login(username='testuser', password='testpass123')

        # Выходим
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        # Проверяем, что доступ к странице, требующей авторизации, перенаправляет
        response = self.client.get(reverse('favourites'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class FavouriteIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='favouriteuser', password='pass123')
        self.game = Game.objects.create(
            name="Игра для избранного",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )
        self.client.login(username='favouriteuser', password='pass123')

    def test_5_add_to_favourite(self):
        response = self.client.get(reverse('add_to_favourite', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)

        favourite = FavouriteGame.objects.filter(user=self.user, game=self.game).first()
        self.assertIsNotNone(favourite)

    def test_6_favourite_appears_in_favourites_page(self):
        FavouriteGame.objects.create(user=self.user, game=self.game)

        response = self.client.get(reverse('favourites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Игра для избранного")

    def test_7_remove_from_favourite(self):
        fav = FavouriteGame.objects.create(user=self.user, game=self.game)

        response = self.client.get(reverse('remove_from_favourite', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(FavouriteGame.objects.filter(id=fav.id).exists())


class FullUserWorkflowTest(TestCase):
    """Полный пользовательский сценарий"""

    def test_8_complete_user_workflow(self):
        """Тест 8: Полный цикл - регистрация, вход, добавление в избранное"""
        client = Client()

        # 1. Регистрация
        register_data = {
            'username': 'workflowuser',
            'password1': 'complex123',
            'password2': 'complex123'
        }
        response = client.post(reverse('register'), register_data)
        self.assertEqual(response.status_code, 302)

        # 2. Вход
        login_data = {
            'username': 'workflowuser',
            'password': 'complex123'
        }
        response = client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)

        # 3. Создаем игру
        game = Game.objects.create(
            name="Workflow Game",
            developer="Dev",
            producer="Pub",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

        # 4. Добавляем в избранное
        response = client.get(reverse('add_to_favourite', args=[game.id]))
        self.assertEqual(response.status_code, 302)

        # 5. Проверяем избранное
        response = client.get(reverse('favourites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Workflow Game")