from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'alphabet'

router = DefaultRouter()

router.register(r'letters', views.LetterListView, basename='letters')
router.register(r'learned', views.LearnedLetterViewSet, basename='learned')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'learned/delete-all/',
        views.LearnedLetterViewSet.as_view({'delete': 'delete_all'}),
        name='learned-delete-all'
    ),
]
