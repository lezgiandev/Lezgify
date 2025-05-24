from django.urls import path
from .views import TranslateAndTTSView, TTSOnlyView

app_name = 'translator'


urlpatterns = [
    path('app/', TranslateAndTTSView.as_view(), name='translator'),
    path('tts/', TTSOnlyView.as_view(), name='tts'),
]