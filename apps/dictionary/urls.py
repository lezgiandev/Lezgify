from rest_framework import routers
from . import views
from django.urls import (
    path,
    include
)

app_name = 'dictionary'

router = routers.DefaultRouter()

router.register(r'categories', views.DictionaryCategoryViewSet, basename='category')
router.register(r'parts-of-speech', views.PartOfSpeechViewSet, basename='part-of-speech')
router.register(r'words', views.DictionaryViewSet, basename='word')
router.register(r'favorites', views.FavoriteWordViewSet, basename='favorite')
router.register(r'learned', views.LearnedWordViewSet, basename='learned')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'words/<int:pk>/translations/',
        views.DictionaryViewSet.as_view({'get': 'translations'}),
        name='word-translations'
    ),
    path(
        'favorites/delete-all/',
        views.FavoriteWordViewSet.as_view({'delete': 'delete_all'}),
        name='favorite-delete-all'
    ),
    path(
        'learned/delete-all/',
        views.LearnedWordViewSet.as_view({'delete': 'delete_all'}),
        name='learned-delete-all'
    ),
]
