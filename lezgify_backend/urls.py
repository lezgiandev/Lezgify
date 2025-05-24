from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/dictionary/', include('apps.dictionary.urls')),
    path('api/alphabet/', include('apps.alphabet.urls')),
    path('api/translator/', include('apps.translator.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/phrasebook/', include('apps.phrasebook.urls')),
    path('api/sources/', include('apps.sources.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
