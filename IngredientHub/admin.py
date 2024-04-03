from django.contrib import admin
from .models import (Category, Subcategory, GroceryProduct, Recipe, RecipeIngredient)

# Register your models here.

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(GroceryProduct)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category_id')
    list_display_links = ('name', 'parent_category_id')

class GroceryProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category_id',
        'sub_category_id',
        'description',
        'image_url',
    )
    list_display_links = (
        'name',
        'category_id',
        'sub_category_id',
        'description',
        'image_url',
    )

class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'ingredients',
        'duration',
        'image_url',
        'user',
        'created_date',
    )
    list_display_links = (
        'title',
        'description',
        'ingredients',
        'duration',
        'image_url',
        'user',
        'created_date',
    )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'quantity',
        'unit',
    )
    list_display_links = (
        'recipe',
        'ingredient',
        'quantity',
        'unit',
    )