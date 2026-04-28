from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Listing


def home(request):
    return render(request, 'market/home.html')


class ListingListView(ListView):
    model = Listing
    template_name = 'market/listing_list.html'
    context_object_name = 'listings'


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'market/listing_detail.html'
    context_object_name = 'listing'


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = 'market/listing_form.html'
    fields = ['category', 'title', 'description', 'price', 'location', 'image']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner_id == self.request.user.id


class ListingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Listing
    template_name = 'market/listing_form.html'
    fields = ['category', 'title', 'description', 'price', 'location', 'image']


class ListingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Listing
    template_name = 'market/listing_confirm_delete.html'
    success_url = reverse_lazy('listing_list')
