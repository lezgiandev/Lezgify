from django.contrib import admin
from .models import (
    Category,
    Word,
    Translation,
    PartOfSpeech,
    Origin
)


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    can_delete = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(PartOfSpeech)
class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )
    ordering = ('name',)


@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')
    search_fields = ('language', )
    ordering = ('language',)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'part_of_speech', 'category')
    list_filter = ('category',)
    search_fields = ('text', 'category__name', 'part_of_speech__name')
    inlines = [TranslationInline]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'word', 'text', 'audio', 'origin')
    search_fields = ('text', 'word__text')
    list_filter = ('origin',)
