from collections import Counter
from django.db import models  # Добавьте эту строку в начало файла
from .models import Game, FavouriteGame, Review

class GameRecommender:
    """
    Класс для рекомендации игр на основе избранного пользователя
    Алгоритм:
    1. Находим игры из избранного пользователя
    2. Ищем другие игры с похожими характеристиками (жанр, разработчик)
    3. Учитываем оценки других пользователей
    4. Сортируем по релевантности
    """


    def __init__(self, user):
        self.user = user
        self.favourite_games = FavouriteGame.objects.filter(user=user).select_related('game')
        self.favourite_game_ids = [fg.game.id for fg in self.favourite_games]

    def get_recommendations(self, limit=10):
        """Получить рекомендации для пользователя"""
        if not self.favourite_games.exists():
            return Game.objects.all().order_by('?')[:limit]  # Случайные игры

        # Собираем характеристики из избранных игр
        favourite_games = [fg.game for fg in self.favourite_games]

        # Считаем частоту жанров в избранном
        genres = [game.genre for game in favourite_games]
        genre_counter = Counter(genres)

        # Считаем частоту разработчиков
        developers = [game.developer for game in favourite_games]
        dev_counter = Counter(developers)

        # Получаем все игры, кроме избранных
        other_games = Game.objects.exclude(id__in=self.favourite_game_ids)

        # Оцениваем каждую игру
        scored_games = []
        for game in other_games:
            score = 0

            # Бонус за совпадение жанра
            if game.genre in genre_counter:
                score += genre_counter[game.genre] * 10

            # Бонус за совпадение разработчика
            if game.developer in dev_counter:
                score += dev_counter[game.developer] * 15

            # Бонус за высокий рейтинг
            avg_rating = game.get_average_rating()
            if avg_rating:
                score += avg_rating * 5

            # Бонус за количество отзывов
            review_count = game.reviews.count()
            score += review_count * 2

            scored_games.append((game, score))

        # Сортируем по убыванию оценки и возвращаем топ
        scored_games.sort(key=lambda x: x[1], reverse=True)
        return [game for game, score in scored_games[:limit]]

    def get_similar_games(self, game, limit=5):
        """Найти игры похожие на указанную"""
        # Ищем игры того же жанра или разработчика
        similar = Game.objects.filter(
            models.Q(genre=game.genre) | models.Q(developer=game.developer)
        ).exclude(id=game.id).exclude(id__in=self.favourite_game_ids)

        # Оцениваем похожесть
        scored = []
        for g in similar:
            score = 0
            if g.genre == game.genre:
                score += 30
            if g.developer == game.developer:
                score += 50
            if g.year == game.year:
                score += 20
            scored.append((g, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [g for g, s in scored[:limit]]


def get_popular_games(limit=10):
    """Получить популярные игры (по количеству в избранном и отзывам)"""
    games = Game.objects.all()
    scored = []

    for game in games:
        popularity = (
                game.favourite_games.count() * 3 +
                game.reviews.count() * 2 +
                game.get_average_rating() * 5
        )
        scored.append((game, popularity))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [game for game, score in scored[:limit]]


def get_trending_games(days=7, limit=10):
    """Получить трендовые игры (добавленные в избранное за последние дни)"""
    from django.utils import timezone
    from datetime import timedelta

    recent = timezone.now() - timedelta(days=days)
    trending_games = Game.objects.filter(
        favourite_games__dt_created__gte=recent
    ).annotate(
        recent_fav_count=models.Count('favourite_games')
    ).order_by('-recent_fav_count')[:limit]

    return trending_games