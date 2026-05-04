from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView

from .forms import ListingForm, RegisterForm
from .models import Category, Listing


def home(request):
    return render(request, 'market/home.html')


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Your account was created. You are now signed in.')
        return redirect(self.get_success_url())


class ListingListView(ListView):
    model = Listing
    template_name = 'market/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 9

    def get_queryset(self):
        sort = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['price', '-price', '-created_at', 'created_at', 'title']
        if sort not in valid_sorts:
            sort = '-created_at'
        self._sort = sort

        qs = Listing.objects.select_related('category', 'owner').order_by(sort)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        category = self.request.GET.get('category', '').strip()
        if category.isdigit():
            qs = qs.filter(category_id=int(category))

        min_price = self.request.GET.get('min_price', '').strip()
        if min_price:
            try:
                qs = qs.filter(price__gte=Decimal(min_price))
            except (InvalidOperation, ValueError):
                pass

        max_price = self.request.GET.get('max_price', '').strip()
        if max_price:
            try:
                qs = qs.filter(price__lte=Decimal(max_price))
            except (InvalidOperation, ValueError):
                pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '').strip()
        selected_category = self.request.GET.get('category', '').strip()
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        sort = getattr(self, '_sort', '-created_at')

        ctx['categories'] = Category.objects.all().order_by('name')
        ctx['q'] = q
        ctx['selected_category'] = selected_category
        ctx['min_price'] = min_price
        ctx['max_price'] = max_price
        ctx['sort'] = sort

        def build_query(*, include_category: bool, include_price: bool) -> str:
            parts = []
            if q:
                parts.append(('q', q))
            if include_category and selected_category:
                parts.append(('category', selected_category))
            if include_price and min_price:
                parts.append(('min_price', min_price))
            if include_price and max_price:
                parts.append(('max_price', max_price))
            parts.append(('sort', sort))
            return urlencode(parts)

        ctx['listing_query'] = build_query(include_category=True, include_price=True)
        ctx['listing_query_no_cat'] = build_query(include_category=False, include_price=True)
        ctx['listing_query_no_price'] = build_query(include_category=True, include_price=False)
        return ctx


def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('category', 'owner'),
        pk=pk,
    )
    related = (
        Listing.objects.filter(category=listing.category)
        .exclude(pk=listing.pk)
        .select_related('category')
        .order_by('-created_at')[:3]
    )
    return render(
        request,
        'market/listing_detail.html',
        {'listing': listing, 'related': related},
    )


@login_required
def profile(request):
    user_listings = (
        Listing.objects.filter(owner=request.user)
        .select_related('category')
        .order_by('-created_at')
    )
    return render(request, 'market/profile.html', {'user_listings': user_listings})


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
