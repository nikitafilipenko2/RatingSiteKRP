from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from PIL import Image  # для обработки изображений
import os

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
    comment = models.TextField('Комментарий', max_length=1000, blank=True)  # Новое поле
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='reviews', verbose_name='Игра')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reviews', verbose_name='Пользователь')
    dt_created = models.DateTimeField('Дата создания', auto_now_add=True)  # Добавим дату создания
    dt_updated = models.DateTimeField('Дата обновления', auto_now=True)    # Добавим дату обновления

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['game', 'user'], name='unique_review_per_user_game')
        ]
        ordering = ['-dt_created']  # Сортировка по дате (сначала новые)

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


class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    bio = models.TextField('О себе', max_length=500, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', default='avatars/default.jpg', blank=True)
    location = models.CharField('Местоположение', max_length=100, blank=True)
    website = models.URLField('Веб-сайт', max_length=200, blank=True)
    telegram = models.CharField('Telegram', max_length=50, blank=True)
    discord = models.CharField('Discord', max_length=50, blank=True)

    # Статистика
    games_rated = models.IntegerField('Оценено игр', default=0)
    reviews_count = models.IntegerField('Написано отзывов', default=0)
    favourite_count = models.IntegerField('В избранном', default=0)

    # Даты
    dt_created = models.DateTimeField('Дата создания', auto_now_add=True)
    dt_updated = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Оптимизация аватара (уменьшение размера)
        if self.avatar and os.path.exists(self.avatar.path):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                print(f"Error processing avatar: {e}")

    def update_stats(self):
        """Обновление статистики пользователя"""
        self.reviews_count = self.user.reviews.count()
        self.favourite_count = self.user.favourite_games.count()
        # Здесь можно добавить подсчет оцененных игр
        self.save()


# Сигнал для автоматического создания профиля при создании пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создание профиля при регистрации пользователя"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранение профиля при сохранении пользователя"""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

def update_stats(self):
    """Обновление статистики пользователя"""
    self.reviews_count = self.user.reviews.count()
    self.favourite_count = self.user.favourite_games.count()
    # Подсчитываем уникальные игры, которые пользователь оценил
    self.games_rated = self.user.reviews.values('game').distinct().count()
    self.save()