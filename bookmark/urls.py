from django.urls import path
from django.conf.urls import url
from bookmark import views

urlpatterns = [
    path('', views.HomeListView.as_view(), name='bookmark-home'),
    path('bookmarks', views.BookmarksListView.as_view(), name='bookmark-bookmarks'),
    path('visited', views.VisitedListView.as_view(), name='bookmark-visited'),
    url(r'^add-to-visited', views.AddToVisitedView.as_view(), name='add-to-visited'),
    url(r'^add-to-bookmarks', views.AddToBookmarksView.as_view(), name='add-to-bookmarks')
]