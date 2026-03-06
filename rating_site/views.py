from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Game, FavouriteGame
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Game
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Profile, Game, Review, FavouriteGame
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Game, Review
from .forms import ReviewForm

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


def profile(request, username):
    """Просмотр профиля пользователя"""
    user = get_object_or_404(User, username=username)

    # Получаем статистику
    reviews = Review.objects.filter(user=user).select_related('game')[:5]
    favourites = FavouriteGame.objects.filter(user=user).select_related('game')[:5]

    # Обновляем статистику в профиле
    try:
        profile = user.profile
        profile.update_stats()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    context = {
        'profile_user': user,
        'profile': profile,
        'reviews': reviews,
        'favourites': favourites,
        'reviews_count': Review.objects.filter(user=user).count(),
        'favourites_count': FavouriteGame.objects.filter(user=user).count(),
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование своего профиля"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile_edit.html', context)


@login_required
def profile_reviews(request, username):
    """Все отзывы пользователя"""
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(user=user).select_related('game').order_by('-id')

    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'title': f'Отзывы пользователя {user.username}'
    }
    return render(request, 'profile_reviews.html', context)


@login_required
def profile_favourites_full(request, username):
    """Все избранные игры пользователя"""
    user = get_object_or_404(User, username=username)
    favourites = FavouriteGame.objects.filter(user=user).select_related('game').order_by('-dt_created')

    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(favourites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'title': f'Избранное пользователя {user.username}'
    }
    return render(request, 'profile_favourites.html', context)


@login_required
def add_review(request, game_id):
    """Добавление или редактирование отзыва"""
    game = get_object_or_404(Game, id=game_id)

    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_review = Review.objects.filter(game=game, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.game = game
            review.user = request.user
            review.save()

            # Обновляем статистику в профиле
            try:
                request.user.profile.update_stats()
            except:
                pass

            if existing_review:
                messages.success(request, 'Отзыв успешно обновлен!')
            else:
                messages.success(request, 'Отзыв успешно добавлен!')

            return redirect('game_detail', game_id=game.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ReviewForm(instance=existing_review)

    context = {
        'form': form,
        'game': game,
        'is_edit': existing_review is not None
    }
    return render(request, 'add_review.html', context)


@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    game_id = review.game.id
    review.delete()

    # Обновляем статистику в профиле
    try:
        request.user.profile.update_stats()
    except:
        pass

    messages.success(request, 'Отзыв успешно удален!')
    return redirect('game_detail', game_id=game_id)


@login_required
def edit_review(request, review_id):
    """Редактирование отзыва (альтернативный метод)"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    return add_review(request, review.game.id)  # Перенаправляем на ту же форму