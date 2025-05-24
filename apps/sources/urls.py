from rest_framework import routers
from . import views
from django.urls import (
    path,
    include
)

app_name = 'sources'

router = routers.DefaultRouter()

router.register(r'categories', views.SourceCategoryViewSet, basename='category')
router.register(r'all', views.SourceViewSet, basename='source')
router.register(r'marked', views.MarkedSourceViewSet, basename='marked')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'marked/delete-all/',
        views.MarkedSourceViewSet.as_view({'delete': 'delete_all'}),
        name='favorite-delete-all'
    )
]
