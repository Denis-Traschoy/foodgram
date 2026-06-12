from django.contrib import admin

from .models import Favorite, Recipe, RecipeIngredient, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'cooking_time', 'pub_date']
    list_filter = ['tags', 'pub_date']
    search_fields = ['name', 'author__email']
    autocomplete_fields = ['author', 'tags']
    inlines = [RecipeIngredientInline]
    readonly_fields = ['pub_date']


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipe', 'ingredient', 'amount']
    search_fields = ['recipe__name', 'ingredient__name']
    autocomplete_fields = ['recipe', 'ingredient']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__email', 'recipe__name']
    autocomplete_fields = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__email', 'recipe__name']
    autocomplete_fields = ['user', 'recipe']
