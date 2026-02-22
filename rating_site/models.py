from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Game(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    developer = models.CharField('Разработчик', max_length=100)
    producer = models.CharField('Издатель', max_length=100)
    operating_system = models.CharField('Операционная система', max_length=100)
    genre = models.CharField('Жанр', max_length=100)
    year = models.DateField('Дата выпуска')

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

    def __str__(self):
        return self.name


class Review(models.Model):
    score = models.IntegerField(
        'Оценка',
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='reviews', verbose_name='Игра')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reviews', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['game', 'user'], name='unique_review_per_user_game')
        ]

    def __str__(self):
        return f'{self.game.name} - {self.user} - {self.score}'


class FavouriteGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='favourite_games', verbose_name='Пользователь')
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='favourite_games', verbose_name='Игра')
    dt_created = models.DateTimeField('Дата создания', auto_now_add=True)
    dt_updated = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Любимая игра'
        verbose_name_plural = 'Любимые игры'
        constraints = [
            models.UniqueConstraint(fields=['user', 'game'], name='unique_favourite_per_user_game')
        ]

    def __str__(self):
        return f'{self.user} -> {self.game}'