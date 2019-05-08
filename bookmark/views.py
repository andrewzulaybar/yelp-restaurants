from django.shortcuts import render

from bookmark.api import bookmarks as bm, restaurants


def home(request):
    return render(request, 'bookmark/home.html', {'title': 'Home Page', 'restaurants': restaurants.RESTAURANTS})


def bookmarks(request):
    return render(request, 'bookmark/bookmarks.html', {'title': 'Bookmarks', 'restaurants': bm.RESTAURANTS})
