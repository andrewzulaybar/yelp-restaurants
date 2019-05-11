from django.shortcuts import render

from bookmark.api import bookmarks as bm, restaurants, visited as vis


def home(request):
    return render(request, 'bookmark/home.html', {'title': 'Home Page', 'restaurants': restaurants.RESTAURANTS})


def bookmarks(request):
    return render(request, 'bookmark/bookmarks.html', {'title': 'Bookmarks', 'restaurants': bm.RESTAURANTS})


def visited(request):
    return render(request, 'bookmark/visited.html', {'title': 'Visited', 'restaurants': vis.RESTAURANTS})
