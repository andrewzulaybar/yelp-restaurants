from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='bookmark-home'),
    path('bookmarks', views.bookmarks, name='bookmark-bookmarks'),
    path('visited', views.visited, name='bookmark-visited')
]