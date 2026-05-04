from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ListingForm
from .models import Listing


def home(request):
    return render(request, 'market/home.html')


class ListingListView(ListView):
    model = Listing
    template_name = 'market/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related('category', 'owner')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'market/listing_detail.html'
    context_object_name = 'listing'


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'market/listing_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner_id == self.request.user.id


class ListingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = 'market/listing_form.html'


class ListingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Listing
    template_name = 'market/listing_confirm_delete.html'
    success_url = reverse_lazy('listing_list')
