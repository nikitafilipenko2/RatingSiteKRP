from django.contrib import admin
from .models import Game, Review, FavouriteGame


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'producer', 'genre', 'year')
    list_filter = ('genre', 'developer', 'year')
    search_fields = ('name', 'developer', 'producer')
    ordering = ('-year', 'name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'score')
    list_filter = ('score', 'game')
    search_fields = ('game__name', 'user__username')
    ordering = ('game', 'user')


@admin.register(FavouriteGame)
class FavouriteGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'dt_created', 'dt_updated')
    list_filter = ('dt_created', 'dt_updated')
    search_fields = ('user__username', 'game__name')
    ordering = ('-dt_created',)
