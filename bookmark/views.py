from django.shortcuts import render

from bookmark import restaurants


def home(request):
    return render(request, 'bookmark/home.html', {'title': 'Home Page', 'restaurants': restaurants.RESTAURANTS})
