from django.contrib import messages
from django.core import exceptions
from django.shortcuts import render, redirect

from bookmark.api import bookmarks as bm, restaurants, visited as vis
from bookmark.forms import BookmarkForm, VisitedForm
from bookmark.models import Restaurant


def home(request):
    return render(request, 'bookmark/home.html', {'title': 'Home Page', 'restaurants': restaurants.RESTAURANTS})


def bookmarks(request):
    return render(request, 'bookmark/bookmarks.html', {'title': 'Bookmarks', 'restaurants': bm.RESTAURANTS})


def visited(request):
    return render(request, 'bookmark/visited.html', {'title': 'Visited', 'restaurants': vis.RESTAURANTS})


def add_to_visited(request):
    # If this is a POST request we need to process the form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request:
        form = VisitedForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            # Save name and business_id
            name = form.cleaned_data.get('name')
            business_id = form.cleaned_data.get('business_id')

            # Attempt retrieval of object from database
            try:
                r = Restaurant.objects.filter(business_id=business_id).get()
                if r.visited:
                    # Object is already in visited, display warning message
                    messages.warning(request, f'{name} is already in your visited list!')
                    return redirect('bookmark-home')
                else:
                    # Object is in bookmarks, move to visited and remove from bookmarks
                    r.visited = True
                    r.bookmark = False
                    r.save()
            except exceptions.ObjectDoesNotExist:
                # Object does not yet exist, save to database
                form.save()

            # Display success message
            messages.success(request, f'Added {name} to visited!')
        else:
            # Form is invalid (i.e. missing fields), display error message
            messages.error(request, 'An error occurred! Please try again later.', extra_tags='danger')

        # Redirect user to the previous page and display alerts
        return redirect(request.META.get('HTTP_REFERER'))


def add_to_bookmarks(request):
    # If this is a POST request we need to process the form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request:
        form = BookmarkForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            # Save name and business_id
            name = form.cleaned_data.get('name')
            business_id = form.cleaned_data.get('business_id')

            # Attempt retrieval of object from database
            try:
                r = Restaurant.objects.filter(business_id=business_id).get()
                if r.bookmark:
                    # Object is already in bookmarks, display warning message
                    messages.warning(request, f'{name} is already in your bookmarks list!')
                else:
                    # Object is in visited, display warning message
                    messages.warning(request, f'{name} is in your visited list!')
            except exceptions.ObjectDoesNotExist:
                # Object does not yet exist, save to database and display success message
                form.save()
                messages.success(request, f'Added {name} to visited!')
        else:
            # Form is invalid (i.e. missing fields), display error message
            messages.error(request, 'An error occurred! Please try again later.', extra_tags='danger')

        # Redirect user to home page and display alerts
        return redirect('bookmark-home')
