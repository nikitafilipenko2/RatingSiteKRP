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

    return render(request, 'game_detail.html', {
        'game': game,
        'reviews': reviews
    })


@login_required
def favourites(request):
    favourite_games = request.user.favourite_games.select_related('game').all()

    return render(request, 'favourites.html', {
        'favourites': favourite_games
    })


@login_required
def add_to_favourite(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    # Проверяем, есть ли уже в избранном
    favourite_exists = FavouriteGame.objects.filter(
        user=request.user,
        game=game
    ).exists()

    if favourite_exists:
        # Если есть - удаляем
        FavouriteGame.objects.filter(user=request.user, game=game).delete()
        messages.success(request, f'Игра "{game.name}" удалена из избранного')
    else:
        # Если нет - добавляем
        FavouriteGame.objects.create(user=request.user, game=game)
        messages.success(request, f'Игра "{game.name}" добавлена в избранное')

    # Возвращаемся на страницу игры
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

    return render(request, 'register.html', {
        'form': form
    })


@login_required
def remove_from_favourite(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    favourite = get_object_or_404(FavouriteGame, user=request.user, game=game)
    favourite.delete()
    messages.success(request, f'Игра "{game.name}" удалена из избранного')

    # Возвращаемся на предыдущую страницу или в избранное
    next_page = request.META.get('HTTP_REFERER', 'favourites')
    return redirect(next_page)