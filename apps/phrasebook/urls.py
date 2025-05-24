from rest_framework import routers
from . import views
from django.urls import (
    path,
    include
)

app_name = 'phrasebook'

router = routers.DefaultRouter()

router.register(r'categories', views.PhrasebookCategoryViewSet, basename='category')
router.register(r'phrases', views.PhrasebookViewSet, basename='phrase')
router.register(r'favorites', views.FavoritePhraseViewSet, basename='favorite')
router.register(r'learned', views.LearnedPhraseViewSet, basename='learned')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'phrases/<int:pk>/translations/',
        views.PhrasebookViewSet.as_view({'get': 'translations'}),
        name='phrase-translations'
    ),
    path(
        'favorites/delete-all/',
        views.FavoritePhraseViewSet.as_view({'delete': 'delete_all'}),
        name='favorite-delete-all'
    ),
    path(
        'learned/delete-all/',
        views.LearnedPhraseViewSet.as_view({'delete': 'delete_all'}),
        name='learned-delete-all'
    ),
]
