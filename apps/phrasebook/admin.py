from django.contrib import admin
from .models import (
    Category,
    Phrase,
    Translation
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


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'category')
    list_filter = ('category',)
    search_fields = ('text', 'category__name')
    inlines = [TranslationInline]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'phrase', 'text', 'audio')
    search_fields = ('text', 'phrase__text')
    list_filter = ('phrase',)
