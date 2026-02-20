from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'producer', 'genre', 'year')
    list_filter = ('genre', 'developer', 'year')
    search_fields = ('name', 'developer', 'producer')
    ordering = ('-year', 'name')
