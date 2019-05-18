from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView

from bookmark.forms import DeleteForm
from bookmark.models import Restaurant


class DeleteView(FormView):
    form_class = DeleteForm

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        business_id = form.cleaned_data.get('business_id')

        # Delete business from database, display success image, and refresh page
        Restaurant.objects.filter(business_id=business_id).delete()
        messages.success(self.request, f'Successfully deleted {name}!')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def form_invalid(self, form):
        # Display error message and refresh page
        messages.error(self.request, 'An error occurred! Please try again later.', extra_tags='danger')
        return redirect(self.request.META.get('HTTP_REFERER'))
