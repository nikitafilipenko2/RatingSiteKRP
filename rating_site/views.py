from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Game, FavouriteGame
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Game


def home(request):
    # Получаем все игры, сортируем по названию
    games_list = Game.objects.all().order_by('name')

    # Пагинация: 10 игр на страницу
    paginator = Paginator(games_list, 10)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'games': games,
        'title': 'Каталог игр'
    })


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    reviews = game.reviews.all()

    return render(request, 'rating_site/game_detail.html', {
        'game': game,
        'reviews': reviews
    })


@login_required
def favourites(request):
    favourite_games = request.user.favourite_games.select_related('game').all()

    return render(request, 'rating_site/favourites.html', {
        'favourites': favourite_games
    })


@login_required
def add_to_favourite(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    # Проверяем, нет ли уже в избранном
    favourite, created = FavouriteGame.objects.get_or_create(
        user=request.user,
        game=game
    )

    if created:
        messages.success(request, f'Игра "{game.name}" добавлена в избранное')
    else:
        messages.info(request, f'Игра "{game.name}" уже в избранном')

    return redirect('game_detail', game_id=game_id)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'rating_site/register.html', {
        'form': form
    })