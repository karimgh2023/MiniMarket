from django.contrib import admin

from .models import Category, Listing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'created_at']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description', 'location']
    list_filter = ['category', 'created_at']
    list_display = ['title', 'category', 'owner', 'price', 'created_at']
