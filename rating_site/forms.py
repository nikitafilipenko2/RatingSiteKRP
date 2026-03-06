from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""
    email = forms.EmailField(label='Email', required=False)
    first_name = forms.CharField(label='Имя', max_length=30, required=False)
    last_name = forms.CharField(label='Фамилия', max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Имя пользователя',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов.',
        }


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления профиля"""

    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'avatar', 'location', 'website', 'telegram', 'discord']
        labels = {
            'bio': 'О себе',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
            'location': 'Местоположение',
            'website': 'Веб-сайт',
            'telegram': 'Telegram',
            'discord': 'Discord',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе...'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'telegram': forms.TextInput(attrs={'placeholder': '@username'}),
            'discord': forms.TextInput(attrs={'placeholder': 'username#0000'}),
        }


from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма для создания/редактирования отзыва"""

    class Meta:
        model = Review
        fields = ['score', 'comment']
        labels = {
            'score': 'Оценка',
            'comment': 'Комментарий',
        }
        widgets = {
            'score': forms.NumberInput(attrs={
                'min': 0,
                'max': 10,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв об игре...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
        help_texts = {
            'score': 'Оцените игру от 0 до 10',
        }