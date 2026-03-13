from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rating_site.admin import admin_site
urlpatterns = [
    # Главная
    path('', views.home, name='home'),
    path('games/', views.home, name='games_list'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Профиль - ВАЖНО: специфичные маршруты должны быть перед <str:username>
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/reviews/', views.profile_reviews, name='profile_reviews'),
    path('profile/<str:username>/favourites/', views.profile_favourites_full, name='profile_favourites_full'),
    path('profile/<str:username>/', views.profile, name='profile'),

    # Игры
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),

    # Избранное
    path('favourites/', views.favourites, name='favourites'),
    path('add-to-favourite/<int:game_id>/', views.add_to_favourite, name='add_to_favourite'),
    path('remove-from-favourite/<int:game_id>/', views.remove_from_favourite, name='remove_from_favourite'),

    path('game/<int:game_id>/add-review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('admin/', admin_site.urls),
]