from django.urls import path
from django.conf.urls import url
from bookmark import views

urlpatterns = [
    path('', views.HomeListView.as_view(), name='bookmark-home'),
    path('bookmarks', views.BookmarksListView.as_view(), name='bookmark-bookmarks'),
    path('visited', views.VisitedListView.as_view(), name='bookmark-visited'),
    url(r'^add-to-bookmarks', views.bookmarks.AddToBookmarksView.as_view(), name='add-to-bookmarks'),
    url(r'^add-to-visited', views.visited.AddToVisitedView.as_view(), name='add-to-visited'),
    url(r'^delete', views.DeleteView.as_view(), name='delete'),
    url(r'^bookmarks/sort-by-distance', views.SortByDistance.as_view(), name='sort-by-distance'),
    url(r'^bookmarks/sort-by-popularity', views.SortByPopularity.as_view(), name='sort-by-popularity'),
    url(r'^bookmarks/sort-by-rating', views.SortByRating.as_view(), name='sort-by-rating'),
    url(r'^bookmarks/sort-by-cuisine', views.SortByCuisine.as_view(), name='sort-by-cuisine'),
    url(r'^bookmarks/is-open-now', views.IsOpenNow.as_view(), name='is-open-now')
]
