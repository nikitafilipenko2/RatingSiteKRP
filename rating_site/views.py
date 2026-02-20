from django.shortcuts import render

from rating_site.models import Game


def home(request):
    games_list = Game.objects.all()
    context = {
        'games_list': games_list,
    }
    return render(request, 'home.html', context)
