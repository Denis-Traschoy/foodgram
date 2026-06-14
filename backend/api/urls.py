from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, ShortLinkRedirectView, TagViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('users.urls')),  # логин/логаут
    path(
        's/<str:short_link>/',
        ShortLinkRedirectView.as_view(),
        name='short-link'
    ),
]
