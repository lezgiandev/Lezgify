from rest_framework import routers
from . import views
from django.urls import (
    path,
    include
)

app_name = 'library'

router = routers.DefaultRouter()

router.register(r'categories', views.BookCategoryViewSet, basename='category')
router.register(r'books', views.LibraryViewSet, basename='book')
router.register(r'completed', views.CompletedBookViewSet, basename='completed')
router.register(r'bookmarks', views.BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'books/<int:pk>/sentences/',
        views.LibraryViewSet.as_view({'get': 'sentences'}),
        name='book-sentences'
    ),
    path(
        'completed/delete-all/',
        views.CompletedBookViewSet.as_view({'delete': 'delete_all'}),
        name='completed-delete-all'
    ),
    path(
        'bookmarks/delete-all/',
        views.BookmarkViewSet.as_view({'delete': 'delete_all'}),
        name='bookmarks-delete-all'
    )
]
