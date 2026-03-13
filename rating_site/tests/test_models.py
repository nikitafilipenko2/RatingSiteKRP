from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from rating_site.models import Game, Review, Profile, FavouriteGame
from datetime import date


class GameModelTest(TestCase):
    """Модульные тесты для модели Game"""

    def test_game_creation(self):
        """Тест 1: Создание игры"""
        game = Game.objects.create(
            name="Тестовая игра",
            developer="Тестовый разработчик",
            producer="Тестовый издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )
        self.assertEqual(game.name, "Тестовая игра")
        self.assertEqual(game.developer, "Тестовый разработчик")

    def test_game_str_method(self):
        """Тест 2: Строковое представление игры"""
        game = Game.objects.create(
            name="Super Game",
            developer="Dev",
            producer="Pub",
            operating_system="Windows",
            genre="Action",
            year=date(2023, 1, 1)
        )
        self.assertEqual(str(game), "Super Game")

    def test_game_unique_name_constraint(self):
        """Тест 3: Уникальность названия игры"""
        Game.objects.create(
            name="Уникальная игра",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

        with self.assertRaises(Exception):
            Game.objects.create(
                name="Уникальная игра",
                developer="Другой",
                producer="Другой",
                operating_system="Linux",
                genre="Action",
                year=date(2024, 1, 1)
            )


class ReviewModelTest(TestCase):
    """Модульные тесты для модели Review"""

    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="pass123")
        self.game = Game.objects.create(
            name="Игра для отзывов",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

    def test_review_creation_with_comment(self):
        """Тест 4: Создание отзыва с комментарием"""
        review = Review.objects.create(
            score=9,
            comment="Отличная игра!",
            game=self.game,
            user=self.user
        )
        self.assertEqual(review.score, 9)
        self.assertEqual(review.comment, "Отличная игра!")

    def test_review_creation_without_comment(self):
        review = Review.objects.create(
            score=7,
            comment="",
            game=self.game,
            user=self.user
        )
        self.assertEqual(review.score, 7)
        self.assertEqual(review.comment, "")

    def test_review_str_method(self):
        """Тест 6: Строковое представление отзыва"""
        review = Review.objects.create(
            score=8,
            comment="Неплохо",
            game=self.game,
            user=self.user
        )
        expected = f"{self.game.name} - {self.user.username} - 8"
        self.assertEqual(str(review), expected)

    def test_unique_review_per_user_game(self):
        """Тест 7: Один пользователь - один отзыв на игру"""
        Review.objects.create(
            score=8,
            game=self.game,
            user=self.user
        )

        with self.assertRaises(IntegrityError):
            Review.objects.create(
                score=9,
                game=self.game,
                user=self.user
            )


class ProfileModelTest(TestCase):
    """Модульные тесты для модели Profile"""

    def test_profile_auto_creation(self):
        """Тест 8: Профиль создается автоматически при регистрации"""
        user = User.objects.create_user(username="newuser", password="pass123")
        profile = Profile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user.username, "newuser")