from django.urls import path
from django.conf.urls import url
from bookmark import views

urlpatterns = [
    path('', views.HomeListView.as_view(), name='home'),
    path('bookmarks', views.BookmarksListView.as_view(), name='bookmarks'),
    path('visited', views.VisitedListView.as_view(), name='visited'),
    url(r'^add-to-bookmarks', views.SaveView.as_view(), name='add-to-bookmarks'),
    url(r'^add-to-visited', views.SaveView.as_view(), name='add-to-visited'),
    url(r'^delete', views.DeleteView.as_view(), name='delete'),
    url(r'^search', views.Search.as_view(), name='search')
]
