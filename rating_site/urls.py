from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.home, name='games_list'),  # временно ведет на home
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('favourites/', views.favourites, name='favourites'),
    path('add-to-favourite/<int:game_id>/', views.add_to_favourite, name='add_to_favourite'),
    path('login/', auth_views.LoginView.as_view(template_name='rating_site/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]