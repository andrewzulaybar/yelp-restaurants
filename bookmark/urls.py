from django.urls import path
from django.conf.urls import url
from bookmark import views

urlpatterns = [
    path('', views.home, name='bookmark-home'),
    path('bookmarks', views.bookmarks, name='bookmark-bookmarks'),
    path('visited', views.visited, name='bookmark-visited'),
    url(r'^', views.add_to_visited, name='add-to-visited')
]