from django.contrib import admin

from bookmark.models import *

admin.site.register(Bookmarks)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Restaurant)
admin.site.register(RestaurantHasCategory)
admin.site.register(Visited)
