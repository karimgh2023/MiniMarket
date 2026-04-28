from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.ListingListView.as_view(), name='listing_list'),
    path('listings/new/', views.ListingCreateView.as_view(), name='listing_create'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('listings/<int:pk>/edit/', views.ListingUpdateView.as_view(), name='listing_update'),
    path('listings/<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing_delete'),
]

