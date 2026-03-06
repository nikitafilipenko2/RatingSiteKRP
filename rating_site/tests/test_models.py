from django.test import TestCase
from django.contrib.auth.models import User
from rating_site.models import Game, Review, Profile, FavouriteGame
from datetime import date


class ProfileModelTest(TestCase):
    """Один основной тест для модели Profile"""

    def test_profile_auto_creation(self):
        """Тест: Профиль автоматически создается при регистрации пользователя"""
        # Создаем пользователя
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # Проверяем, что профиль создался автоматически
        profile = Profile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user.username, "testuser")
        self.assertEqual(profile.bio, "")  # Пустое по умолчанию


class ReviewModelTest(TestCase):
    """Один основной тест для модели Review"""

    def test_review_creation_with_comment(self):
        """Тест: Создание отзыва с комментарием"""
        # Создаем пользователя и игру
        user = User.objects.create_user(username="reviewuser", password="pass123")
        game = Game.objects.create(
            name="Тестовая игра",
            developer="Разработчик",
            producer="Издатель",
            operating_system="Windows",
            genre="RPG",
            year=date(2023, 1, 1)
        )

        # Создаем отзыв
        review = Review.objects.create(
            score=9,
            comment="Отличная игра, очень понравилась!",
            game=game,
            user=user
        )

        # Проверяем
        self.assertEqual(review.score, 9)
        self.assertEqual(review.comment, "Отличная игра, очень понравилась!")
        self.assertEqual(review.game.name, "Тестовая игра")
        self.assertEqual(review.user.username, "reviewuser")