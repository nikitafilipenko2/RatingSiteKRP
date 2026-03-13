from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count, Avg
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .models import Game, Review, FavouriteGame, Profile


class GameRatingAdminSite(AdminSite):
    site_header = 'GameRating Администрирование'
    site_title = 'GameRating Admin'
    index_title = 'Панель управления'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_view(self.statistics_view), name='statistics'),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        # Общая статистика
        total_games = Game.objects.count()
        total_users = User.objects.count()
        total_reviews = Review.objects.count()
        total_favourites = FavouriteGame.objects.count()

        # Игры с наибольшим количеством отзывов
        top_reviewed_games = Game.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:10]

        # Игры с наивысшим средним рейтингом
        games_with_ratings = []
        for game in Game.objects.all():
            avg_rating = game.get_average_rating()
            if avg_rating > 0:
                games_with_ratings.append((game, avg_rating))

        top_rated_games = sorted(games_with_ratings, key=lambda x: x[1], reverse=True)[:10]

        # Самые популярные игры (в избранном)
        top_favourite_games = Game.objects.annotate(
            fav_count=Count('favourite_games')
        ).order_by('-fav_count')[:10]

        # Статистика по жанрам
        genre_stats = Game.objects.values('genre').annotate(
            count=Count('id'),
            avg_rating=Avg('reviews__score')
        ).order_by('-count')

        # Активность пользователей
        top_users = User.objects.annotate(
            review_count=Count('reviews'),
            favourite_count=Count('favourite_games')
        ).order_by('-review_count')[:10]

        context = {
            'total_games': total_games,
            'total_users': total_users,
            'total_reviews': total_reviews,
            'total_favourites': total_favourites,
            'top_reviewed_games': top_reviewed_games,
            'top_rated_games': top_rated_games,
            'top_favourite_games': top_favourite_games,
            'genre_stats': genre_stats,
            'top_users': top_users,
        }

        return TemplateResponse(request, 'admin/statistics.html', context)


admin_site = GameRatingAdminSite(name='myadmin')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'producer', 'genre', 'year', 'rating_display', 'favourites_count')
    list_filter = ('genre', 'year', 'developer')
    search_fields = ('name', 'developer', 'producer')
    readonly_fields = ('rating_display', 'favourites_count', 'reviews_list')

    def rating_display(self, obj):
        avg = obj.get_average_rating()
        if avg:
            stars = '★' * int(avg) + '☆' * (10 - int(avg))
            return format_html(
                '<span style="color: gold;">{}</span> {:.1f}/10',
                stars, avg
            )
        return 'Нет оценок'

    rating_display.short_description = 'Рейтинг'

    def favourites_count(self, obj):
        count = obj.get_favourites_count()
        return format_html('<b>{}</b>', count)

    favourites_count.short_description = 'В избранном'

    def reviews_list(self, obj):
        reviews = obj.reviews.all()[:5]
        html = '<ul>'
        for review in reviews:
            html += f'<li>{review.user.username}: {review.score}/10 - {review.comment[:50]}...</li>'
        html += '</ul>'
        if obj.reviews.count() > 5:
            html += f'<p>... и ещё {obj.reviews.count() - 5} отзывов</p>'
        return format_html(html)

    reviews_list.short_description = 'Последние отзывы'

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="games.csv"'

        writer = csv.writer(response)
        writer.writerow(['Название', 'Разработчик', 'Издатель', 'Жанр', 'Год', 'Рейтинг'])

        for game in queryset:
            writer.writerow([
                game.name,
                game.developer,
                game.producer,
                game.genre,
                game.year.year,
                game.get_average_rating()
            ])

        return response

    export_as_csv.short_description = "Экспортировать выбранные игры в CSV"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'score', 'comment_short', 'dt_created')
    list_filter = ('score', 'dt_created')
    search_fields = ('game__name', 'user__username', 'comment')
    readonly_fields = ('dt_created', 'dt_updated')

    def comment_short(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment

    comment_short.short_description = 'Комментарий'

    actions = ['delete_selected']


@admin.register(FavouriteGame)
class FavouriteGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'dt_created')
    list_filter = ('dt_created',)
    search_fields = ('user__username', 'game__name')
    readonly_fields = ('dt_created', 'dt_updated')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'reviews_count', 'favourite_count', 'games_rated')
    list_filter = ('location',)
    search_fields = ('user__username', 'bio')
    readonly_fields = ('reviews_count', 'favourite_count', 'games_rated', 'dt_created', 'dt_updated')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'bio', 'birth_date', 'avatar')
        }),
        ('Контакты', {
            'fields': ('location', 'website', 'telegram', 'discord')
        }),
        ('Статистика', {
            'fields': ('reviews_count', 'favourite_count', 'games_rated')
        }),
        ('Даты', {
            'fields': ('dt_created', 'dt_updated')
        }),
    )